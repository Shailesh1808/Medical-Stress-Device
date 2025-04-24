import time
import threading
from datetime import datetime
from models import db, SensorData
from ecg_reader import read_ecg
from gsr_reader import read_gsr
from report_utils import generate_single_report
import numpy as np

def collect_sensor_data(user_id, duration_seconds=60, app=None):
    with app.app_context():
        print(f"🟢 Starting 60s data collection for user {user_id}...")

        ecg_hr_list = []
        ecg_hrv_list = []
        ecg_arrhythmia_flags = []

        gsr_mean_list = []
        gsr_peak_list = []

        gsr_initial = None
        gsr_final = None

        stop_event = threading.Event()

        def ecg_worker():
            nonlocal ecg_hr_list, ecg_hrv_list, ecg_arrhythmia_flags
            while not stop_event.is_set():
                hr, hrv, flag = read_ecg(duration_sec=10)
                ecg_hr_list.append(hr)
                ecg_hrv_list.append(hrv)
                ecg_arrhythmia_flags.append(flag)
                time.sleep(2)

        def gsr_worker():
            nonlocal gsr_mean_list, gsr_peak_list, gsr_initial, gsr_final
            while not stop_event.is_set():
                mean, peaks, _ = read_gsr(duration_sec=2)
                gsr_mean_list.append(mean)
                gsr_peak_list.append(peaks)

                if gsr_initial is None:
                    gsr_initial = mean
                gsr_final = mean
                time.sleep(2)

        # Start threads
        ecg_thread = threading.Thread(target=ecg_worker)
        gsr_thread = threading.Thread(target=gsr_worker)
        ecg_thread.start()
        gsr_thread.start()

        time.sleep(duration_seconds)  # Wait 60s

        stop_event.set()
        ecg_thread.join()
        gsr_thread.join()

        valid_hr = [x for x in ecg_hr_list if x is not None]
        valid_hrv = [x for x in ecg_hrv_list if x is not None]

        # Aggregate values
        avg_hr = float(np.mean(ecg_hr_list)) if valid_hr else None
        avg_hrv = float(np.mean(ecg_hrv_list)) if valid_hrv else None
        any_arrhythmia = any(ecg_arrhythmia_flags)

        avg_gsr = float(np.mean(gsr_mean_list)) if gsr_mean_list else None
        total_peaks = int(np.sum(gsr_peak_list)) if gsr_peak_list else 0
        gsr_trend = (gsr_final - gsr_initial) if gsr_initial and gsr_final else 0.0

        # Create record
        record = SensorData(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            heart_rate=avg_hr,
            hrv=avg_hrv,
            arrhythmia_flag=any_arrhythmia,
            gsr_mean=avg_gsr,
            gsr_peak_count=total_peaks,
            gsr_trend=gsr_trend,
            notes=None
        )

        try:
            # Call GPT for analysis
            record.notes = generate_single_report(record)
        except Exception as e:
            print(f"⚠️ GPT failed: {e}")
            record.notes = "GPT report unavailable."

        db.session.add(record)
        db.session.commit()

        print("✅ Final summarized data saved with GPT report.")