from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy
import cv2
import cv2.aruco as aruco
from aruco_lib import *
import os

def bot_align(image):    #for aligning the bot after the color detection
    kernel = np.ones((5, 5), np.uint8)
    #color_range=np.array([[84, 166, 114],[169, 248, 245]]) blue
    color_range=np.array([[65, 75, 49],[112, 147, 152]]) #green
    # convert the frame to HSV co-ordinates
    frame = cv2.imread(image)
    cv2.imshow("image",frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # mask -> to apply filter to the image based on color range
    mask = cv2.inRange(hsv, color_range[0], color_range[1])
    print(color_range[0])
    
    # erode -> to remove small blobs in the image
    mask = cv2.erode(mask, kernel, iterations=1)
    # dilate -> to sharpen the edges
    mask = cv2.dilate(mask, kernel, iterations=1)
    cv2.imshow("mask",mask)
    cv2.waitKey(0)
    # contours -> set of points which are in white
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if contours:
        # maximum area -> the ball
        object = max(contours, key=len)
        # calculating the x-center and y-center
        (x, y) = ((max(object[:, :, 0])+min(object[:, :, 0]))//2, (max(object[:, :, 1])+min(object[:, :, 1]))//2) 
    return (x-320)

# Camera
resolution = (640, 480)                   # resolution for the frame
camera = PiCamera()                       # To initialize the PiCamera
camera.resolution = resolution            # set the resolution of the camera
camera.framerate = 16                     # Set the frame rate
rawCapture = PiRGBArray(camera, size=resolution) 
camera.rotation = 270


camera.start_preview()
camera.capture("align.jpg")
rawCapture.truncate(0)
#print(bot_align("align.jpg"))
camera.stop_preview()

cv2.destroyAllWindows()
