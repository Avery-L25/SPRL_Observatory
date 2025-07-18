#!/usr/bin/env python3

import os
from datetime import date, datetime
import numpy as np  # * testing
import cv2  # type: ignore
import h5py

thedate = date.today()

rasdir = "where the files are stored"
folder = thedate.strftime('%y%B')
file = thedate.strftime('%d_%m_%y.txt')

wdir = os.getcwd()


def file_check(file1, file2, wdir):
    cpath1 = f"{wdir}/{file1}"
    cpath2 = f"{wdir}/{file1}"
    print(cpath1)
    print(cpath2)
    if os.path.exists(cpath1):
        if os.path.splitext(cpath1)[1] == '.txt':
            print("GOOD")
        else:
            print(os.path.splitext(cpath1)[1])
    else:
        print("this sucks")
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        content1 = f1.read()
        content2 = f2.read()
        if content1 == content2:
            print("Files are identical.")
        else:
            print("Files differ.")


# test 1: txt/csv
def test1():
    with open(f"{file}", 'w') as t:
        t.write(f"{np.random.randint(0, 2, [10, 10])}")

    file2 = f"test{file}"
    os.system(f"cp {file} {file2}")

    file_check(file, file2, wdir)
    file2 = f"test{file}"
    os.system(f"cp {file} {file2}")
    # test 2
    with open(f"{file}", 'w') as t:
        t.write(f"{wdir}")

    file_check(file, file2, wdir)


# test 2: images  NOTE: this  is its own test!!!! #!!!!!!!!!!!!!!
def test2():
    img1 = cv2.imread('Lena.jpg')
    img2 = cv2.imread('Lena.jpg')
    if img1.all() == img2.all():
        print('sameimage (1 and 2)')
    else:
        print('for some reason this is wrong')

    img3 = cv2.imread('hubble-space-telescope-hst-6.webp')

    if img1.all() == img3.all():
        print('sameimage')
    else:
        print('good, they arent the same (1 and 3)')


# test 3: hdf
def create_hdf5_file(file_name):

    """Creates an HDF5 file and writes random data."""

    with h5py.File(file_name, "w") as f:
        data = np.random.rand(100, 100)
        f.create_dataset("random_data", data=data)
    print(f"{file_name} created successfully.")


def hdf5_check(file1, file2, wdir):
    cpath1 = f"{wdir}/{file1}"
    cpath2 = f"{wdir}/{file1}"
    print(cpath1)
    print(cpath2)
    if os.path.exists(cpath1):
        if os.path.splitext(cpath1)[1] == '.txt':
            print("GOOD")
        else:
            print(os.path.splitext(cpath1)[1])
    else:
        print("this sucks")

    with h5py.File(file1, 'r') as f1, h5py.File(file2, 'r') as f2:
        data = {}
        for f in [f1, f2]:
            keys = list(f.keys())
            print(keys[0])
            data[f] = {}
            for i in keys:
                data[i] = f[i][()]

            print(data)

        if data[f1] == data[f2]:
            print("Files are identical.")
        else:
            print("Files differ.")


def test3():
    hdf1 = 'test1.hdf5'
    create_hdf5_file('test1.hdf5')
    hdf2 = hdf1
    hdf3 = 'test3.hdf5'
    create_hdf5_file('test3.hdf5')
    hdf5_check(hdf1, hdf2, wdir)
    hdf5_check(hdf1, hdf3, wdir)


#   hdf5_check('test1.hdf5', 'test3.hdf5', wdir)
#    with h5py.File('test1.hdf5', 'r') as fr1:
# keys = list(fr1.keys())
# print(keys[0])
# data = fr1['random_data'][()]
# print(data)

# region This is for testing the scheduling modules

import schedule as sched
from ischedule import run_loop, schedule
import time 
from datetime import datetime
def time1():
    z = 2
    y= datetime.now()
    print('this is test 1')
    print(f'z = {z}')
    # time.sleep(2)


def time2():
    y= datetime.now()
    print('test 2')
    # time.sleep(5)


def switch():
    global z
    print('switch')
    if z ==2:
        z = 10
    elif z == 10:
        z = 2
    else:
        z =2

z = 2
x = 0
l = 1




lol = None

if lol is None:
    lol = 0
elif lol < 12:
    lol = 14
elif lol >= 12:
    lol = None




okay = False

while okay is True:

    if x >= 6:
        sched.cancel_job(time2)
        sched.every(2).seconds.do(time1)
        l = 2
    else:
        sched.cancel_job(time2)
        sched.every(5).seconds.do(time2)
        l = 5
    sched.run_pending()
    time.sleep(1)
    x += 1
    print(x)
