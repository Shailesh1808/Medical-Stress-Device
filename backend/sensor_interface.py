import time
from datetime import datetime
from models import db, SensorData
import numpy as np
import random

from ecg_reader import read_ecg
from report_utils import generate_single_report

# Used to track GSR trend from last window
last_gsr = None

def detect_gsr_peaks(gsr_window):
    """Simple peak count in GSR window."""
    peaks = 0
    for i in range(1, len(gsr_window) - 1):
        if gsr_window[i] > gsr_window[i-1] and gsr_window[i] > gsr_window[i+1]:
            peaks += 1
    return peaks

def collect_sensor_data(user_id, duration_seconds=60, app=None):
    with app.app_context():
        print(f"🟢 [START] Collecting sensor data for user_id={user_id} for {duration_seconds}s")
        start_time = time.time()
        global last_gsr

        while time.time() - start_time < duration_seconds:
            # === 1. Read ECG ===
            heart_rate, hrv, arrhythmia_flag = read_ecg(duration_sec=10)

            # === 2. Simulated GSR block (to be replaced with real GSR read) ===
            gsr_window = [random.uniform(0.6, 1.0) for _ in range(5)]
            gsr_mean = np.mean(gsr_window)
            gsr_peaks = detect_gsr_peaks(gsr_window)
            gsr_trend = (gsr_mean - last_gsr) if last_gsr is not None else 0
            last_gsr = gsr_mean

            # === 3. Store to DB ===
            data = SensorData(
                user_id=user_id,
                timestamp=datetime.utcnow(),
                heart_rate=heart_rate,
                hrv=hrv,
                arrhythmia_flag=arrhythmia_flag,
                gsr_mean=gsr_mean,
                gsr_peak_count=gsr_peaks,
                gsr_trend=gsr_trend,
                notes=None
            )
            db.session.add(data)
            db.session.commit()

            # === 4. Generate GPT report based on this row ===
            try:
                data.notes = generate_single_report(data)
                db.session.commit()
            except Exception as e:
                print(f"⚠️ GPT report failed: {e}")

            # === 5. Log Output ===
            hr_str = f"{heart_rate:.1f}" if heart_rate is not None else "N/A"
            hrv_str = f"{hrv:.1f}" if hrv is not None else "N/A"
            print(f"✅ ECG: HR={hr_str} BPM, HRV={hrv_str} ms | GSR={gsr_mean:.2f} | Peaks={gsr_peaks}")

            time.sleep(2)

        print("🛑 [END] Data collection complete.")
