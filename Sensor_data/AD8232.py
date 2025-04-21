import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# Set up I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADS1115 ADC object
ads = ADS1115(i2c)

# Choose the input channel (A0 in this case)
ecg_channel = AnalogIn(ads, ADS1115.P0)

# Optional: Set the gain (adjust based on your signal strength)
ads.gain = 1  # 2/3, 1, 2, 4, 8, 16

print("Reading ECG data from AD8232 via ADS1115...")
print("Press Ctrl+C to stop.")

try:
    while True:
        voltage = ecg_channel.voltage  # in Volts
        print(f"ECG Voltage: {voltage:.4f} V")
        time.sleep(0.01)  # 100Hz sampling (adjust as needed)
except KeyboardInterrupt:
    print("Stopped ECG data reading.")
