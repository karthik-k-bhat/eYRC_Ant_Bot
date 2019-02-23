import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

resolution = (640, 480)

camera = PiCamera()
camera.resolution = resolution
camera.framerate = 32
camera.rotation = 270
rawCapture = PiRGBArray(camera, size=resolution)

time.sleep(0.1)
