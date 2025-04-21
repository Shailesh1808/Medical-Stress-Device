import time
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as plt
import board
import busio

# Initialize I2C and ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
adc = ADS1115(i2c)
GAIN = 1  # Gain setting for the ADS1115 (adjust based on your input voltage range)

# Initialize AnalogIn for channel A1
gsr_channel = AnalogIn(adc, 1)  # Channel 1 corresponds to A1

# Initialize plot
plt.ion()
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot(x_data, y_data, label="A1 Voltage")
ax.set_xlim(0, 10)  # Adjust as needed
ax.set_ylim(-0.5, 5.5)  # Adjust based on expected voltage range
ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage (V)")
ax.legend()

start_time = time.time()

try:
    while True:
        # Read voltage from channel A1
        voltage = gsr_channel.voltage  # Automatically converts raw ADC value to voltage

        # Update plot data
        current_time = time.time() - start_time
        x_data.append(current_time)
        y_data.append(voltage)
        line.set_xdata(x_data)
        line.set_ydata(y_data)

        # Adjust plot limits dynamically
        ax.set_xlim(0, max(10, current_time))
        ax.set_ylim(min(y_data) - 0.5, max(y_data) + 0.5)

        # Redraw plot
        plt.pause(0.1)

except KeyboardInterrupt:
    print("Exiting...")
    plt.ioff()
    plt.show()
    