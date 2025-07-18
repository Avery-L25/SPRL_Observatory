import h5py
import glob
import numpy as np


def build_hdf(date, gps, temp, pres, mag, img, hdf_path):
    print('build hdf')
    with h5py.File(hdf_path, "w") as f:
        f.create_dataset("date", maxshape=(None,), dtype=h5py.string_dtype(),
                         data=[date])
        f.create_dataset("gps", maxshape=(None,), dtype='f', data=[gps])
        f.create_dataset("temperature", maxshape=(None, 2), dtype='f',
                         data=[temp])
        f.create_dataset("pressure", maxshape=(None,), dtype='f', data=[pres])
        f.create_dataset("magnetic field", maxshape=(None, 3), dtype='f',
                         data=[mag])
        f.create_dataset("aurora img", maxshape=(None, 512, 512, 3),
                         dtype='uint8', data=[img])


def add_data(date, gps, temp, pres, mag, img, hdf_path):
    print('add data')
    with h5py.File(hdf_path, "a") as f:
        f["date"].resize((f["date"].shape[0] + 1), axis=0)
        f['date'][-1] = date
        f["gps"].resize((f["gps"].shape[0] + 1), axis=0)
        f["gps"][-1:] = gps
        f["temperature"].resize((f["temperature"].shape[0] + 1), axis=0)
        f['temperature'][-1] = temp
        f["pressure"].resize((f["pressure"].shape[0] + 1), axis=0)
        f['pressure'][-1] = pres
        f["magnetic field"].resize((f["magnetic field"].shape[0] + 1), axis=0)
        f['magnetic field'][-1] = mag
        f["aurora img"].resize((f["aurora img"].shape[0] + 1), axis=0)
        f['aurora img'][-1] = img


def hdf(mag, pres, temp, gps, img, hdf_path):
    d_t = np.datetime64('now').item().strftime('%Y_%m_%d_%H_%M_%S')
    if glob.glob("*.hdf5"):
        add_data(d_t, gps, temp, pres, mag, img)
    else:
        build_hdf(d_t, gps, temp, pres, mag, img)
