import time
import board
import busio
import numpy as np

from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1115 import ADS1115

# Last GSR value for computing trend
last_gsr_mean = None

def detect_gsr_peaks(gsr_window):
    peaks = 0
    for i in range(1, len(gsr_window) - 1):
        if gsr_window[i] > gsr_window[i - 1] and gsr_window[i] > gsr_window[i + 1]:
            peaks += 1
    return peaks

def read_gsr(duration_sec=10, sampling_rate=5):
    global last_gsr_mean
    print(f"🧪 Reading GSR for {duration_sec} seconds...")

    # 🔁 Move these inside the function
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS1115(i2c)
    chan = AnalogIn(ads, 0)

    interval = 1.0 / sampling_rate
    num_samples = int(duration_sec * sampling_rate)
    gsr_values = []

    for _ in range(num_samples):
        raw_val = chan.value
        gsr_values.append(raw_val)
        time.sleep(interval)

    gsr_values = np.array(gsr_values)
    gsr_mean = float(np.mean(gsr_values))
    gsr_peak_count = detect_gsr_peaks(gsr_values.tolist())
    gsr_trend = gsr_mean - last_gsr_mean if last_gsr_mean is not None else 0.0
    last_gsr_mean = gsr_mean

    print(f"✅ GSR Done: Mean={gsr_mean:.2f}, Peaks={gsr_peak_count}, Trend={gsr_trend:.2f}")
    return gsr_mean, gsr_peak_count, gsr_trend