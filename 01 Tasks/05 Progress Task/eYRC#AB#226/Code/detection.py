'''
* Team Id          : 226
* Author List      : Suryanarayan
* Filename         : detection.py
* Theme            : Ant Bot
* Functions        : detect_sim_id 
* Global Variables : aruco_id
'''

#Import packages
import numpy
import cv2
import cv2.aruco as aruco
from aruco_lib import *
import os

aruco_id = None

'''
* Function Name : detect_sim_id
* Input         : Path to the image file
* Output        : Aruco ID - Integer 
* Logic         : Detects the Arcuo Ids if present in the given Image file.
                  Returns None if no Aruco is detected. Uses Aruco library provided by the e-Yantra team
* Example Call  : detect_sim_id("Image.jpg")
'''
def detect_sim_id(path_to_image):
    global aruco_id
    img = cv2.imread(path_to_image) #give the name of the image with the complete path
    det_aruco_list = {}
    det_aruco_list = detect_Aruco(img)  #calling detect_Aruco from the aruco library
    #print(det_aruco_list)
    if det_aruco_list:
        aruco_id = list(det_aruco_list.keys())[0] #taking only the id value
        return aruco_id
