import datetime
import numpy as np
from ischedule import run_loop, schedule
from Data_processing.image_processing import Image
from Data_processing.hdf import hdf
from Data_processing.transmission.file_transmission_2 import upload_file_to_drive
from Sensors.barom_therm_data_collection import temp_n_pres
from Sensors.mag_data import mag_data
from Sensors.camera.shot import shot

T = 10
camera_period = 0 # a counter for camera's period 
img = Image(np.zeros((512, 512, 3)))
cur_day = datetime.date.today()

folder_id = "1o4uRjhgtwmRvK-3zxdAHeIlSxOJW4nqL"
hdf_path = 'test.hdf5'

def cam_off():  # Turn off the cam
    None

def read_data(cam_flag):    # instruct sensors to read current data
    # None will be replaced to be the sensor's program
    mag = mag_data()
    temp, pres = temp_n_pres()
#    temp, pres, mag = [None]*2, None, [None]*3
    gps = None

    if cam_flag:    # separate cam reading due to different frequency from sensors
        img = shot()#np.ones((512, 512, 3))
    else:
        img = np.zeros((512, 512, 3))
    return mag, pres, temp, gps, img

def timer():
    global T, camera_period, img, cur_day
 
    if (datetime.date.today() - cur_day).days <= 0: # new day
#        upload_file_to_drive(hdf_path, folder_id)
        cur_day = datetime.date.today()

    if datetime.datetime.now().hour > 18:   # Can be skipped if there is no new img
        if img.aurora_detection():  # if there is aurora detected
            T = 10
            print('no aurora')
        else:
            T = 5*60
            print('aurora present')
    else:
        cam_off()
        print('daytime')

    camera_period += 10
        

def data_processing():
    global T, camera_period
    if camera_period >= T:  # it the time to take picture
        camera_period = 0
        img.pre = img.img
    mag, pres, temp, gps, img.img = read_data(not bool(camera_period))
    img.resize()
    img.aurora_detection()
    hdf(mag, pres, temp, gps, img.img)  # input data into database

if __name__ == '__main__':
    # run the program with period = 10 sec
#    schedule(timer, interval=2)
    schedule(data_processing, interval=2)  
    run_loop(return_after=3)
    
#    upload_file_to_drive(hdf_path, folder_id)
    

