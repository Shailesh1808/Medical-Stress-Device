import time
import numpy as np
from scipy.signal import find_peaks
from board import SCL, SDA
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# === I2C + ADC Setup ===
i2c = busio.I2C(SCL, SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
ecg_channel = AnalogIn(ads, ADS.P0)

def read_ecg(duration_sec=10, sample_rate=250):
    """Reads ECG signal, calculates HR (BPM), HRV (ms), arrhythmia flag."""
    print(f"🩺 Starting ECG read for {duration_sec}s...")

    num_samples = duration_sec * sample_rate
    ecg_signal = []

    # === Signal Acquisition ===
    while len(ecg_signal) < num_samples:
        voltage = ecg_channel.voltage
        ecg_signal.append(voltage)
        time.sleep(1 / sample_rate)

    ecg_array = np.array(ecg_signal)

    # === R-peak Detection ===
    threshold = np.mean(ecg_array) + 0.1
    peaks, _ = find_peaks(ecg_array, distance=sample_rate * 0.5, height=threshold)

    # === BPM and HRV Calculation ===
    rr_intervals = np.diff(peaks) / sample_rate  # seconds
    bpm_list = 60 / rr_intervals if len(rr_intervals) > 0 else []
    heart_rate = np.mean(bpm_list) if len(bpm_list) > 0 else None
    hrv = np.std(rr_intervals) * 1000 if len(rr_intervals) > 1 else None  # HRV in ms

    # === Simple Arrhythmia Check ===
    arrhythmia_flag = hrv is not None and hrv < 15

    return heart_rate, hrv, arrhythmia_flag
