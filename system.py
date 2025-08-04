#!/usr/bin/env python3

# import necessary libraries
import os
import datetime
import time
import glob
import numpy as np
import schedule  # // from ischedule import run_loop, schedule
from Data_processing.image_processing import Image
from Data_processing.hdf import hdf
from Data_processing.transmission.file_transmission_2 import upload_file_to_drive
from Sensors.barom_therm_data_collection import temp_n_pres
from Sensors.mag_data import mag_data
from Sensors.camera.main import shot

# Variable initialization
T = 10  # When to take image
xrun = 5  # todo how often to take data
camera_period = 0  # a counter for camera's period
img = Image(np.zeros((512, 512, 3)))  # blank image
cur_day = datetime.datetime.now(datetime.timezone.utc)
cameraoff = False  # when True camera will not take picutre during the day

# Working directory and file
wdir = os.getcwd()
folder = cur_day.strftime('%y%B')
if cur_day.hour >= 16:
    hdf_file = cur_day.strftime('%d_%m_%y.hdf5')
else:
    cur_day = cur_day - datetime.timedelta(1)
    hdf_file = cur_day.strftime('%d_%m_%y.hdf5')

# GOOGLE AUTHORIZATION
folder_id = "1vgaHd2zrHlnLKV55_ARNKjABrqwS_hxM"  # Dan Wellings Server


# todo 2 paths? the raspi and the one on crabyss


def get_direcs():  # Get working file
    '''
    Calculates the working file name based on UTC time.
    If it is after 4pm UTC a new file name is created for the current day.
    If it is before 4pm UTC the file is the prior day.
    '''
    global folder, hdf_file, cur_day
    now = datetime.datetime.now(datetime.timezone.utc)

    folder = cur_day.strftime('%y%B')
    if now.hour >= 16:
        hdf_file = now.strftime('%d_%m_%y.hdf5')
    else:
        cur_day = now - datetime.timedelta(1)
        hdf_file = cur_day.strftime('%d_%m_%y.hdf5')


def cam_off():  # Turn off the cam
    '''
    Used to turn the camera on/off dependant on the time of day.
    Currently on between 12pm and 7 pm if the function is called.
    '''

    global cameraoff, camera_period
    curtime = datetime.now()
    if curtime.hour > 7 and curtime.hour < 12:
        cameraoff = True
        print('CAMERA OFF')
    else:
        cameraoff = False
        camera_period = 300
        print('CAMERA ON')


def read_data(cam_flag):  # Read data from sensors and camera
    '''
    Runs all the sensors functions to collect data.
    Tales pictures if the cam_flag is true.
    '''

    mag = mag_data()
    temp, pres = temp_n_pres()
    gps = None  # todo complete gps code

    if cam_flag:  # takes an image if the camera period is complete
        img = shot()  # ! check integration of proper shot()
    else:
        img = np.zeros((512, 512, 3), dtype=np.uint8)
    return mag, pres, temp, gps, img


def upload_data():  # Upload data to Google Drive
    '''
    Upload data to the University of Michigans "CRABYSS" server.
    '''
    global hdf_file, folder_id  # ! add path on server
    # if glob.glob("*.hdf5"):
    print('uploading data to the CRABYSS')
    upload_file_to_drive(hdf_file, folder_id)
    # todo os.system(f'rsync -ahP {hdf_path} *USER*@crabyss.engin.umich.edu:{directory to save}') 
    # ! ensure that the delete flag is here unless addressed seperately


def data_processing():  # Collects data, looks for Aurora, Makes HDF
    '''
    Processes data from all sensors and writes it to hdf5 file.
    Determines whether it is time to take a picture.
    Detects an Aurora and updates the camera period accordingly.
    '''
    global T, xrun, camera_period, cameraoff, hdf_file
    if cameraoff is True:
        cam_flag = False
    elif camera_period >= T:  # it the time to take picture
        camera_period = 0
        cam_flag = True
        img.pre = img.img
    else:
        camera_period += xrun  # update counter by the run period
        cam_flag = False
    mag, pres, temp, gps, img.img = read_data(bool(cam_flag))
    img.resize()
    # Check if there us an aurora present
    is_aurora = img.aurora_detection()  # is there an aurora present
    if is_aurora is True:  # if yes, camera takes a photo every 10 seconds
        T = 10
        print('aurora present')
    elif is_aurora is False:  # if no, camera takes a photo every 5 minutes
        T = 300
        print('no aurora')
    hdf(mag, pres, temp, gps, img.img, hdf_file, cam_flag)  # save data to hdf
    cam_flag = False
    # * live_plot.plotting({'x': mag[0],'y': mag[1],'z': mag[2]}, {'in': temp[1], 'out': temp[0]}, pres, img.img, is_aurora)


# initializes scheduling
schedule.every(xrun).seconds.do(data_processing)  # collect data every 'xrun'
schedule.every().day.at("16:00").do(upload_data)  # upload hdf5 file at 4pm
schedule.every().day.at("08:00").do(cam_off)  # turn camera off after 8am
schedule.every().day.at("20:00").do(cam_off)  # turn camera on after 8pm

while __name__ == '__main__':
    # runs any pending programs
    schedule.run_pending()
    time.sleep(1)
