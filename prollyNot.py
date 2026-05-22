#!

from zwo import ZWOASICamera, ZWOASICameraParams
import zwo as cammod
import numpy as np
import cv2 as cv
 
def nothing(x):
    pass
# Let's assume the camera ID is 0 (e.g., only 1 camera is connected):
id = 0

# Create a new camera parameters instance (for demonstration purposes we are
# connecting to a ASI62000M Pro model) which has a pid of "620b":
# N.B. Replace the pid with the correct one for your camera model.
pid: str = "620b"

params: ZWOASICameraParams = ZWOASICameraParams(pid=pid)

# Create a new camera instance:
zwo = ZWOASICamera(id, params)

# Check if the camera is ready:
is_ready = zwo.is_ready()

if not is_ready:
    print("Camera is not ready!")
    exit(1)

raw_img = zwo.get_frame()
zwo._get_video_frame

img_array = np.array(raw_img)
# Create a black image, a window
img = cv.resize(img_array, (255, 255))
cv.namedWindow('image')
 
# create trackbars for color change
cv.createTrackbar('G', 'image', 0, 255, nothing)
cv.createTrackbar('R', 'image', 0, 255, nothing)
cv.createTrackbar('B', 'image', 0, 255, nothing)
 
# create switch for ON/OFF functionality
switch = '0 : OFF \n1 : ON'
cv.createTrackbar(switch, 'image', 0, 1, nothing)
 
while True:
    cv.imshow('image', img)
    k = cv.waitKey(1) & 0xFF
    if k == 27:
        break
 
    # get current positions of four trackbars
    g = cv.getTrackbarPos('G', 'image')
    b = cv.getTrackbarPos('B', 'image')
    r = cv.getTrackbarPos('R', 'image')
    s = cv.getTrackbarPos(switch, 'image')
#    if s == 0:
#    else:
 
#        img[:] = [b,g,r]
#        img[:] = 0
 
cv.destroyAllWindows()