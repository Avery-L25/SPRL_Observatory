#!/usr/bin/env python3

import datetime
import numpy as np
from ischedule import run_loop, schedule
from Data_processing.image_processing import Image
# // from Data_processing.transmission.file_transmission_2 import upload_file_to_drive #NOTE not planning on uploading to drive this is a placeholder
from Data_processing.hdf import hdf
from Sensors.barom_therm_data_collection import temp_n_pres
from Sensors.mag_data import mag_data
from Sensors.camera.main import shot
# from Sensors.camera.shot import shot # ! NOTE: This was the original for testing

# Variable initialization
T = 10  # When to take image
camera_period = 0  # a counter for camera's period
img = Image(np.zeros((512, 512, 3)))  # blank image
cur_day = datetime.date.today()  # keep track of current day
# NOTE: cur_day should be replaced when we have a better method to dump info
# * live_plot = Live_plotting() # in used coded

folder_id = "1o4uRjhgtwmRvK-3zxdAHeIlSxOJW4nqL"  # todo choose folder
hdf_path = 'test.hdf5'  # todo choose path


def cam_off():  # Turn off the cam  # todo turn off camera during the dayS
    None


def read_data(cam_flag):    # instruct sensors to read current data
    # None will be replaced to be the sensor's program
    mag = mag_data()
    temp, pres = temp_n_pres()
    gps = None  # todo complete gps code

    if cam_flag:  # separate cam reading due to different frequency sensors # ! does this work without a camflag ????
        img = shot()  # ! check integration of proper shot()
    else:
        img = np.zeros((512, 512, 3), dtype=np.uint8)
    return mag, pres, temp, gps, img


def timer():   # todo revamp systems for our personal time needs
    global T, camera_period, img, cur_day

    if (datetime.date.today() - cur_day).days <= 0:  # new day
        # upload_file_to_drive(hdf_path, folder_id)  # todo how do we want to upload files???
        cur_day = datetime.date.today()  # todo update when appropriate

    if datetime.datetime.now().hour > 18:  # Can be skipped if no new img
        if img.aurora_detection():  # if there is aurora detected
            T = 10
            print('aurora present')
        else:
            T = 5*60
            print('no aurora')
        #* camera_period += 10
    else:
        cam_off()  # * instead they set # camera_period = 1
        print('daytime')

    camera_period += 10 #* see above


def data_processing():
    global T, camera_period
    if camera_period >= T:  # it the time to take picture
        camera_period = 0
        img.pre = img.img
    mag, pres, temp, gps, img.img = read_data(bool(camera_period))
    img.resize()
    img.aurora_detection() #* added "is_aurora =" to the beginning
    hdf(mag, pres, temp, gps, img.img)  # input data into database
    #* live_plot.plotting({'x': mag[0],'y': mag[1],'z': mag[2]}, {'in': temp[1], 'out': temp[0]}, pres, img.img, is_aurora)


if __name__ == '__main__':
    # run the program with period = XX sec
    # schedule(timer, interval=2) # ! this wasnt used before?????
    schedule(data_processing, interval=2)  # todo choose our intervals
    run_loop(return_after=3)  # todo choose our intervals

    # upload_file_to_drive(hdf_path, folder_id)   # todo our upload
