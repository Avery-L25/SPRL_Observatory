# SPRL_Observatory
Software module for operating a YooperNet Station. Intended for use with the following operations.
An all-sky imager checking for visibile aurora.
Data collection from a magnetometer, thermometer, and barometer.
File management to upload to Google Drive.

## Hardware requirements
Ongoing decisions
-----------
RaspberryPi with Rasbian installed
ZWO ASI Camera
Chip based magnetometer
----------

## Installation/Setup
Installation Script in progress.

Manual Installation:
kinda complicated
1. Install Python 3.12
2. Create venv
3. Install necessary packages from reqs.txt and pkglist.txt
4. **May need to install camera-zwo-asi manually**
5. Camera set-up from cza ....
6. Make startup service with startup script
7. login to google

**Will need to put in google folder id**

## Usage
Intended to automatically run after setup. Will collect data to an **hdf5 file**. 
The YooperNet repository (link) offers operations to interpret data collected by the YooperNet station.
