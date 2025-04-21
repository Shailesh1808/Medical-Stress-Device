import time
import board
import busio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from scipy.signal import find_peaks
import numpy as np

# Constants
SAMPLE_RATE = 250  # Hz
WINDOW_DURATION = 2  # seconds
WINDOW_SIZE = SAMPLE_RATE * WINDOW_DURATION

# Setup I2C for ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
ads.gain = 1
ecg_channel = AnalogIn(ads, 0)

# Initialize ECG data buffer
ecg_data = [0.0] * WINDOW_SIZE
peak_indices = []  # List to track peak locations in the buffer

# Function to detect peaks and return their indices
def detect_peaks(data, fs):
    peaks, _ = find_peaks(data, prominence=0.06, distance=int(0.2 * fs))
    return peaks

# Heart rate from peak timestamps
def calculate_heart_rate_from_peaks(peaks, fs):
    if len(peaks) < 2:
        return 0
    rr_intervals = np.diff(peaks) / fs  # in seconds
    avg_rr = np.mean(rr_intervals)
    return 60 / avg_rr  # BPM

# Real-time plotting setup
fig, ax = plt.subplots()
x_data = list(range(WINDOW_SIZE))
line, = ax.plot(x_data, ecg_data, label="ECG Signal")
peak_dots, = ax.plot([], [], 'ro', label="Detected Peaks")
ax.set_ylim(-0.5, 3.5)
ax.set_xlim(0, WINDOW_SIZE)
ax.set_title("Real-Time ECG Plot")
ax.set_xlabel("Time (samples)")
ax.set_ylabel("Voltage (V)")
ax.legend()

# Update function for the plot
def update(frame):
    global ecg_data, peak_indices

    # Read new ECG value
    ecg_value = ecg_channel.voltage
    ecg_data.append(ecg_value)
    ecg_data.pop(0)

    # Update ECG line
    line.set_ydata(ecg_data)

    # Detect peaks
    peak_indices = detect_peaks(np.array(ecg_data), SAMPLE_RATE)
    peak_dots.set_data(peak_indices, [ecg_data[i] for i in peak_indices])

    # Heart rate calculation every second
    if frame % SAMPLE_RATE == 0:
        hr = calculate_heart_rate_from_peaks(peak_indices, SAMPLE_RATE)
        print(f"❤️ Heart Rate: {hr:.1f} BPM")

    return line, peak_dots

# Start the animation
ani = FuncAnimation(fig, update, interval=1000 / SAMPLE_RATE, blit=True)

try:
    print("Starting real-time ECG plot with heart rate detection...")
    plt.show()
except KeyboardInterrupt:
    print("Exiting...")
