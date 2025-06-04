import time
import board
import busio
import csv
import threading
#from adafruit_bus_device.i2c_device import I2CDevice
import adafruit_lps35hw
import adafruit_sht31d


# Set up I2C and sensor
i2c = board.I2C()  # uses board.SCL and board.SDA

LPS35HW = adafruit_lps35hw.LPS35HW(i2c)
SHT31D = adafruit_sht31d.SHT31D(i2c)

# Variable to control the loop
start_requested = False
stop_requested = False


# Function to listen for "start" command
def listen_for_start():
    global start_requested
    while True:
        command = input("Type 'start' to begin data collection: \n")
        if command.strip().lower() == 'start':
            start_requested = True
            break


# Function to listen for "stop" command
def listen_for_stop():
    global stop_requested
    while True:
        command = input("Type 'stop' to end data collection: \n")
        if command.strip().lower() == "stop":
            stop_requested = True
            break


# Start the stop Listener thread
start_thread = threading.Thread(target=listen_for_start)
start_thread.start()

# Start the stop listener thread
stop_thread = threading.Thread(target=listen_for_stop)
stop_thread.start()

print("Waiting for 'start' command to begin data collection...\n")
while not start_requested:
    time.sleep(1)

print("Data collection started \n")

# Open the CSV file in append mode and add header if it’s empty
with open("BarometerTestData.csv", mode="a", newline='') as data_file:
    writer = csv.writer(data_file)
    # Write header if file is empty
    data_file.seek(0, 2)  # Move to end of file
    if data_file.tell() == 0:
        writer.writerow(["Temperature (C)", "Pressure (hPa)"])

    # Continuously collect and write data until "stop" command is given
    while not stop_requested and start_requested:
        # Read sensor values
        ext_temp = SHT31D.temperature
        int_temp = LPS35HW.temperature
        pressure = LPS35HW.pressure

        # Print to console
        print("Exterior temperature: %.2f C" % ext_temp)
        print("Interior temperature: %.2f C" % int_temp)
        print("Pressure: %.2f hPa" % pressure)
        print("")

        # Write to CSV
        writer.writerow([ext_temp, pressure])

        # Wait 10 seconds
        time.sleep(10)

print("Data collection stopped.")
