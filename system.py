#!/usr/bin/env python3

# import necessary libraries
import os
import datetime
import time
import numpy as np
#// from ischedule import run_loop, schedule
import schedule
from Data_processing.image_processing import Image
# // from Data_processing.transmission.file_transmission_2 import upload_file_to_drive #NOTE not planning on uploading to drive this is a placeholder
from Data_processing.hdf import hdf
from Sensors.barom_therm_data_collection import temp_n_pres
from Sensors.mag_data import mag_data
from Sensors.camera.main import shot
# from Sensors.camera.shot import shot # ! NOTE: This was the original for testing

# Variable initialization
T = 10  # When to take image
xrun = 5  # todo how often to take data
camera_period = 0  # a counter for camera's period
img = Image(np.zeros((512, 512, 3)))  # blank image
cur_day = datetime.date.today()  # keep track of current day
cameraoff = False  # when True camera will not take picutre during the day



# Working directory and file
wdir = os.getcwd()
folder = cur_day.strftime('%y%B')
#// folder_id = "1o4uRjhgtwmRvK-3zxdAHeIlSxOJW4nqL"  # ! this should not be necessary
hdf_path = cur_day.strftime('%d_%m_%y.hdf5')  # ! this should be the file name and hdf_path should become a combination of folder and file when implemented onto raspi
# todo 2 paths? the raspi and the one on crabyss


def cam_off():  # Turn off the cam  # todo turn off camera during the dayS
    global cameraoff
    curtime = datetime.now()
    if curtime.hour > 7 and curtime.hour < 15:
        cameraoff = True
    else:
        cameraoff = False


def read_data(cam_flag):    # instruct sensors to read current data
    # None will be replaced to be the sensor's program
    mag = mag_data()
    temp, pres = temp_n_pres()
    gps = None  # todo complete gps code

    if cam_flag:  # takes an image if the camera period is complete
        img = shot()  # ! check integration of proper shot()
    else:
        img = np.zeros((512, 512, 3), dtype=np.uint8)  # ? can this be made into None and have no information saved???

    return mag, pres, temp, gps, img


def upload_data():
    global hdf_path
    print('uploading data to')
    # todo os.system(f'rsync -ahP {hdf_path} *USER*@crabyss.engin.umich.edu:{directory to save}') 
    #! ensure that the delete flag is here unless addressed seperately

def data_processing():
    global T, xrun, camera_period, cameraoff
    if cameraoff is True:
        cam_flag = False
    elif camera_period >= T:  # it the time to take picture
        camera_period = 0
        cam_flag = True
        img.pre = img.img
    else:
        camera_period += xrun  # update counter by the run period
        cam_flag = False  # ! can be moved to where the camera_period is updated
    mag, pres, temp, gps, img.img = read_data(bool(cam_flag))
    img.resize()
    is_aurora = img.aurora_detection()  # is there an aurora present
    if is_aurora is True:  # if yes, camera takes a photo every 10 seconds
        T = 10
        print('aurora present')
    elif is_aurora is False:  # if no, camera takes a photo every 5 minutes
        T = 300
        print('no aurora')
    hdf(mag, pres, temp, gps, img.img)  # input data into database
    # * live_plot.plotting({'x': mag[0],'y': mag[1],'z': mag[2]}, {'in': temp[1], 'out': temp[0]}, pres, img.img, is_aurora)


# initializes scheduling
schedule.every(xrun).seconds.do(data_processing)  # collect data every 'xrun'
schedule.every().day.at("16:00").do(upload_data)  # upload hdf5 file at 4pm
schedule.every().day.at("08:00").do(cam_off)  # turn camera off after 8am
schedule.every().day.at("20:00").do(cam_off)  # turn camera on after 8pm

if __name__ == '__main__':
    # run the program with period = XX sec
    schedule.run_pending()
    time.sleep(1)
    # schedule(timer, interval=2) # ! this wasnt used before?????
    # //schedule(data_processing, interval=2)  # todo choose our intervals
    # //run_loop(return_after=3)  # todo choose our intervals

    # upload_file_to_drive(hdf_path, folder_id)   # todo our upload
