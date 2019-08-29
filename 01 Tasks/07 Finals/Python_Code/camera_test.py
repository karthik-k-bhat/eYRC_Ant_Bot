import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

resolution = (1920, 1080)

camera = PiCamera()
camera.resolution = resolution
camera.framerate = 32
camera.rotation = 0
rawCapture = PiRGBArray(camera, size=resolution)

time.sleep(0.1)
