# Simple demo of reading the difference between channel
# 1 and 0 on an ADS1x15 ADC.
# Author: Tony DiCola
# License: Public Domain
import time
from datetime import datetime

# Import the ADS1x15 module.
import Adafruit_ADS1x15


# Create an ADS1115 ADC (16-bit) instance.
adc1 = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)
adc2 = Adafruit_ADS1x15.ADS1115(address=0x49, busnum=1)
adc3 = Adafruit_ADS1x15.ADS1115(address=0x4A, busnum=1)
# Or create an ADS1015 ADC (12-bit) instance.
# adc = Adafruit_ADS1x15.ADS1015()

# Note you can change the I2C address from its default (0x48), and/or the I2C
# bus by passing in these optional parameters:
# adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1

print('Press Ctrl-C to quit...')
while True:
    # Read the difference between channel 0 and 1
    # (i.e. channel 0 minus channel 1).
    # Note you can change the differential value to the following:
    #  - 0 = Channel 0 minus channel 1
    #  - 1 = Channel 0 minus channel 3
    #  - 2 = Channel 1 minus channel 3
    #  - 3 = Channel 2 minus channel 3
    sensor_temp = adc1.read_adc_difference(0, gain=GAIN)
    electronics_temp = adc1.read_adc_difference(3, gain=GAIN)
    Bx = adc2.read_adc_difference(0, gain=GAIN)
    By = adc2.read_adc_difference(3, gain=GAIN)
    Bz = adc3.read_adc_difference(0, gain=GAIN)

    # Note you can also pass an optional data_rate parameter above, see
    # simpletest.py and the read_adc function for more information.
    # Value will be a signed 12 or 16 bit integer value (depending on the ADC
    # precision, ADS1015 = 12-bit or ADS1115 = 16-bit).
    print('Sensor Temp: {0}'.format(sensor_temp))
    print('Electronics Temp: {0}'.format(electronics_temp))
    print('Bx: {0}'.format(Bx))
    print('By: {0}'.format(By))
    print('Bz: {0}'.format(Bz))
    print('-----------')

    # Get current time:
    current_time = datetime.utcnow()

    f = open("deployed_test.txt", "a")
    f.write(str(Bx))
    f.write(",")
    f.write(str(By))
    f.write(",")
    f.write(str(Bz))
    f.write(",")
    f.write(str(sensor_temp))
    f.write(",")
    f.write(str(electronics_temp))
    f.write(",")
    f.write(str(current_time))
    f.write("\n")
    f.close()

    f2 = open("//media/pi/4EAD-9E27/deployed_test_usb.txt", "a")
    f2.write(str(Bx))
    f2.write(",")
    f2.write(str(By))
    f2.write(",")
    f2.write(str(Bz))
    f2.write(",")
    f2.write(str(sensor_temp))
    f2.write(",")
    f2.write(str(electronics_temp))
    f2.write(",")
    f2.write(str(current_time))
    f2.write("\n")
    f2.close()

    # Pause for half a second.
    time.sleep(0.5)
