# Program usage: only lines 58 and 73 should be modified by the user to achieve
#                the desired sampling rate. Use the terminal command 
#                'python3 rm3100_spi_write_to_terminal.py > data.txt'
#                to redirect the terminal output into a text file.
#                Text files generated this way are compatible with the Matlab 
#                programs (specifically getdata_pni.m) in the ground-mag-spi GitLab.
import spidev
import time
import datetime
import struct

QRM3100_CMM = 0x01
QRM3100_CCXMSB = 0x04
QRM3100_CCXLSB = 0x05
QRM3100_CCYMSB = 0x06
QRM3100_CCYLSB = 0x07
QRM3100_CCZMSB = 0x08
QRM3100_CCZLSB = 0x09
QRM3100_TMRC = 0x0B
QRM3100_MX2 = 0xA4
QRM3100_MX1 = 0xA5
QRM3100_MX0 = 0xA6
QRM3100_MY2 = 0xA7
QRM3100_MY1 = 0xA8
QRM3100_MY0 = 0xA9
QRM3100_MZ2 = 0xAA
QRM3100_MZ1 = 0xAB
QRM3100_MZ0 = 0xAC
QRM3100_Status = 0xB4

spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 500000

# Set desired cycle count for each axis (default value: 200)
# Range of usable cycle count: 0 - 65536 (recommended: 30-400)
# Relationship: Cycle count and TMRC jointly determines sampling rate.
#               In general, the lower the cycle count, the higher the
#               sampling rate. However, since the maximum sampling rate is
#               determined by the TMRC register, it is possible to have a 
#               very low cycle count and a very low sampling rate at the same time.
#               When sample rate is fixed, lower cycle count will reduce sensor 
#               oscillation time and reduce power consumption, but low cycle count 
#               will also lead to low sensitivity.
# As a demonstration of the effect of cycle count and TMRC, consider the following settings:
# |  TMRC Value  | Cycle Count | Observed Sampling Rate (Hz) |
# |     0x92     |      30     |        484.9372799          |
# |     0x92     |      75     |        406.0053085          |
# |     0x92     |     100     |        308.4930457          |
# |     0x92     |     200     |        157.7277074          |
# |----------------------------------------------------------|
# |     0x96     |      30     |        30.20464953          |
# |     0x96     |     100     |        30.19974251          |
# |     0x96     |     200     |        30.23584211          |
# |     0x96     |    1050     |        30.38722193          |
# |     0x96     |    1500     |        21.45816376          |
# |     0x96     |    2000     |        16.10569605          |
desired_cycle = 200 # change this value to set cycle count for all 3 axes
spi.xfer2([QRM3100_CCXMSB, (desired_cycle & 0xFF00) >> 8])
spi.xfer2([QRM3100_CCXLSB, (desired_cycle & 0x00FF)])
spi.xfer2([QRM3100_CCYMSB, (desired_cycle & 0xFF00) >> 8])
spi.xfer2([QRM3100_CCYLSB, (desired_cycle & 0x00FF)])
spi.xfer2([QRM3100_CCZMSB, (desired_cycle & 0xFF00) >> 8])
spi.xfer2([QRM3100_CCZLSB, (desired_cycle & 0x00FF)])

# Write to TMRC to set MAXIMUM update rates for continuous measurement mode (default setting 0x96)
# Range of accepted TMRC values: 0x92 - 0x9F
# Relationship: the lower the TMRC value, the higher the max sampling rate. The
#               highest nominal max sampling rate is ~600 Hz when using TMRC=0x92.
#               The default setting (TMRC=0x96) has a max sampling rate of ~37 Hz.
#               See Table 5-4: CMM Update Rates on RM3100_Sensor_Suite_User_Manual_r07.pdf
#               for the complete list of maximum sampling rates available.
TMRC = 0x96 # change the hex value to set TMRC
spi.xfer2([QRM3100_TMRC, TMRC]) 

# Initiate continuous measurement mode, which uses the set TMRC value
# as sampling rate to periodically read the values at all 3 axes.
# Set CMM to read all 3 axes, 0x79 is the CMM value needed enable 3-axes reading 
# (as opposed to single axis reading).
spi.xfer2([QRM3100_CMM, 0x79]) 

# Start of output. First 3 lines are used as header (time zone used: UTC)
print('# time (s), B_x, B_y, B_z')
start = datetime.datetime.now()
print('# {} UTC'.format(start))

# As part of the header, print cycle count to ensure raw value to
# nanotesla conversion uses the correct cycle count value
CYCLE_COUNT = spi.xfer2([QRM3100_CCXMSB | 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
print('# Cycle count (x,y,z): {}, {}, {}'.format((CYCLE_COUNT[1] << 8) | CYCLE_COUNT[2], (CYCLE_COUNT[3] << 8) | CYCLE_COUNT[4], (CYCLE_COUNT[5] << 8) | CYCLE_COUNT[6]))

# Helper function for handling negative numbers (2's complement, which the PNI readings are in).
# Python integers use an "infinite" number of bits (ex: 0xFF would be treated as 255, 
# with an infinite number of leading 0's, i.e. 0x00....0FF).
# https://wiki.python.org/moin/BitwiseOperators

# So C style integers are used for the convert_to_signed_int function.
# This function makes use of the struct.pack-unpack functions
# to convert the python int into a signed int in C. The C signed
# int is then shifted and sign extended using C convention.


# Integer structure: byte1 is MSB, byte3 is LSB.
def convert_to_signed_int(byte1, byte2, byte3):
    # Append the 3 PNI bytes into a single 3-byte int then convert into
    # a little-endian (<) C integer (i)
    c_int = struct.pack("<i", (byte1 << 16) | (byte2 << 8) | byte3)

    # Since a C int is 4 bytes and the PNI only supplies 3
    # bytes, c_int's most significant byte is padded.
    # The [:-1] indexing accesses all but the padded MSByte.
    # rjust() appends the c_int with a byte in little endian scheme,
    # effectively shifting c_int left by 8 bits (offsetted by the division by 256).
	
    # ------ Use the following print statements to visualize the above operations ------
    #print ("c_int: ", c_int)
    #print ("c_int[:-1]: ", c_int[:-1])
    #print ("c_int[:-1].rjust(4, b'\x00'): ", c_int[:-1].rjust(4, b'\x00'))
    py_int = int(struct.unpack("<i", c_int[:-1].rjust(4, b'\x00'))[0] / 256)
    return py_int


while True:
    # Ensure measurement is complete on all axes (DRDY pin is set HIGH)
    while (spi.xfer2([QRM3100_Status, 0x00])[1] >> 7) != 1: pass

    # When the host is ready to read the measured values, read from the data registers.
    # readings is a 10-element array containing readings from QRM3100_MX2, QRM3100_MX1, QRM3100_MX0, QRM3100_MY2, ...
    # Note that the first element is an acknowledge and not a reading, so start extracting
    # data from second element onwards
    readings = spi.xfer2([QRM3100_MX2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    x = convert_to_signed_int(readings[1], readings[2], readings[3])
    y = convert_to_signed_int(readings[4], readings[5], readings[6])
    z = convert_to_signed_int(readings[7], readings[8], readings[9])

    now = datetime.datetime.now()

    print('{},{},{},{}'.format(now,x,y,z))
