import time
import board
import busio
import csv
import adafruit_lps35hw
import adafruit_sht31d


# Set up I2C and sensor, assigns data addresses to the sensors automatically
i2c = board.I2C()  # uses board.SCL and board.SDA

LPS35HW = adafruit_lps35hw.LPS35HW(i2c)  # barometer
SHT31D = adafruit_sht31d.SHT31D(i2c)  # Thermometer

with open("BarometerTestData.csv", mode="a", newline='') as data_file:
    writer = csv.writer(data_file)
    # Write header if file is empty
    data_file.seek(0, 2)  # Move to end of file
    if data_file.tell() == 0:
        writer.writerow(["Exterior Temperature (C)", "Pressure (hPa)"])

    # This is an infinite loop, needs a stop condition
    while True:
        # Read sensor values
        ext_temp = SHT31D.temperature  # temperature reading outside the case
        int_temp = LPS35HW.temperature  # temperature reading inside the case
        pressure = LPS35HW.pressure  # pressure reading

        # Write to CSV
        writer.writerow([ext_temp, pressure])

        # Wait 10 seconds then the
        time.sleep(10)
