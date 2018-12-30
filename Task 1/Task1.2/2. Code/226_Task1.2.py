# -*- coding: utf-8 -*-
"""
**************************************************************************
*                  E-Yantra Robotics Competition
*                  ================================
*  This software is intended to check version compatiability of open source software
*  Theme: ANT BOT
*  MODULE: Task1.2
*  Filename: Task1.2.py
*  Version: 1.0.0  
*  Date: October 31, 2018
*  
*  Author: e-Yantra Project, Department of Computer Science
*  and Engineering, Indian Institute of Technology Bombay.
*  
*  Software released under Creative Commons CC BY-NC-SA
*
*  For legal information refer to:
*        http://creativecommons.org/licenses/by-nc-sa/4.0/legalcode 
*     
*
*  This software is made available on an “AS IS WHERE IS BASIS”. 
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or 
*  breach of the terms of this agreement.
*  
*  e-Yantra - An MHRD project under National Mission on Education using 
*  ICT(NMEICT)
*
**************************************************************************
"""

"""
ArUco ID Dictionaries: 4X4 = 4-bit pixel, 4X4_50 = 50 combinations of a 4-bit pixel image
List of Dictionaries in OpenCV's ArUco library:
DICT_4X4_50	 
DICT_4X4_100	 
DICT_4X4_250	 
DICT_4X4_1000	 
DICT_5X5_50	 
DICT_5X5_100	 
DICT_5X5_250	 
DICT_5X5_1000	 
DICT_6X6_50	 
DICT_6X6_100	 
DICT_6X6_250	 
DICT_6X6_1000	 
DICT_7X7_50	 
DICT_7X7_100	 
DICT_7X7_250	 
DICT_7X7_1000	 
DICT_ARUCO_ORIGINAL

Reference: http://hackage.haskell.org/package/opencv-extra-0.2.0.1/docs/OpenCV-Extra-ArUco.html
Reference: https://docs.opencv.org/3.4.2/d9/d6a/group__aruco.html#gaf5d7e909fe8ff2ad2108e354669ecd17
"""

import numpy
import cv2
import cv2.aruco as aruco
from aruco_lib import *
import os


# ------------------ Variables for required for the algorithms -------------------- #
# Tolerances for color
yellow = [(0, 220, 220), (25, 255, 255)]
blue = [(175, 90, 50), (220, 130, 85)]
green = [(0, 160, 35), (20, 200, 75)]
red = [(0, 0, 230), (18, 18, 255)]
orange = [(40, 115, 225), (60, 135, 250)]
# Contour color as specified in rules
contour_color = {red[0] : green[0], green[0] : blue[0], blue[0] : red[0], yellow[0] : orange[0], orange[0] : yellow[0] }
identified_shapes = list()
aruco_id = None
# --------------------------------------------------------------------------------- #

def aruco_detect(path_to_image):
    global image_path, aruco_id
    '''
    you will need to modify the ArUco library's API using the dictionary in it to the respective
    one from the list above in the aruco_lib.py. This API's line is the only line of code you are
    allowed to modify in aruco_lib.py!!!
    '''
    img = cv2.imread(path_to_image)     #give the name of the image with the complete path
    det_aruco_list = {}
    det_aruco_list = detect_Aruco(img)
    if det_aruco_list:
        aruco_id = list(det_aruco_list.keys())[0]
        '''
        Code for triggering color detection on ID detected
        '''
        img = color_detect(img)
        # Mark the Aruco ID on the image
        img = mark_Aruco(img,det_aruco_list)
        state = calculate_Robot_State(img, det_aruco_list)
        # Save the image on the disk
        cv2.imwrite("Output_"+image_path,img)


def color_detect(img):
    global image_path, aruco_id

    for data in image_dict[image_path]:
        # If some shape is to be identified
        if data[0] != None:
            # Get shape details that is to be identified
            shape_details = data
            color = shape_details[0]

            # Perform image processing actions -
            #       1. Masking the image depending on the color - makes it binary color
            mask = cv2.inRange(img, color[0], color[1])
            #       2. Morphological operations on the image to refine the same
            kernel = numpy.ones((5,5),numpy.uint8)
            mask = cv2.dilate(mask, None, iterations=2)             # Dilation
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Closing
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # To find contour in binary image
            contour = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None    
            for unidentified_shape in contour:
                # Function to detect shape
                detect_shape(unidentified_shape, shape_details)
        # If nothing is to be identified
        else:
            identified_shapes.append((None, None, None, None))

    for shapes in identified_shapes:
        if shapes[0] != None:
            centroid = shapes[2]
            cv2.drawContours(img, [shapes[3]], -1, contour_color[shapes[1][0]], 25)
            cv2.putText(img, str(centroid), centroid, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    if os.path.isfile("226_Task1.2.csv"):
        fo = open("226_Task1.2.csv", "a")
    else:
        fo = open("226_Task1.2.csv", "w+")
        fo.write("Image Name," + "ArUco ID" + "," + "(x- y) Object-1" + "," + "(x- y) Object-2" + "\n")

    fo.write(image_path + "," + str(aruco_id) + "," + 
            str(identified_shapes[0][2]).replace(',','-') + "," + 
            str(identified_shapes[1][2]).replace(',','-') + "\n")
    fo.close()

    return img
    

    
def detect_shape(contour, shape_details):
    # Get all the details required
    color = shape_details[0]
    shape = shape_details[1]
    # Calculate the perimeter
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
    
    # Find moment to find centroid
    M = cv2.moments(contour)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    # Using basic knowledge of shapes determine the shape
    # If 3 sides ~ Triangle
    if len(approx) == 3 and shape == "triangle":
        identified_shapes.append(("triangle", color, center, contour))

    # If 4 sides ~ Rectangle
    elif len(approx) == 4 and shape == "square":
        identified_shapes.append(("square", color, center, contour))

    # If many sides are detected ~ Circle or ellipse
    elif len(approx) > 4:
        x_len = int(max(contour[:, :, 0]) - min(contour[:, :, 0]))
        y_len = int(max(contour[:, :, 1]) - min(contour[:, :, 1]))
        
        # If x axis is greater than y axis
        if (x_len > 1.2 * y_len) and shape == "ellipse":
            identified_shape.append(("ellipse", color, center, contour))
        # If both, x axis and y axis are approximately equal
        elif shape == "circle": 
            identified_shapes.append(("circle", color, center, contour))


# ------------- Declare what's to be detected in different images ----------------- #
image_dict = {
              "Image1.jpg" : [(red, "triangle"), (blue, "triangle")], 
              "Image2.jpg" : [(green, "circle"), (red, "circle")],
              "Image3.jpg" : [(None, None), (blue, "square")],
              "Image4.jpg" : [(blue, "square"), (green, "triangle")],
              "Image5.jpg" : [(blue, "circle"), (green, "square")],
              "Aruco_detection.JPG" : [(None, None), (None, None)]
             }
# --------------------------------------------------------------------------------- #

if __name__ == "__main__": 
    # Choose which image to open here. The image has to be in the same folder as the code
    image_path = "Aruco_detection.JPG"
   
    aruco_detect(image_path)