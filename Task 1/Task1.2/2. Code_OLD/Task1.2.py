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

import numpy as np
import cv2
import cv2.aruco as aruco

'''
def aruco_detect(path_to_image):
    
    you will need to modify the ArUco library's API using the dictionary in it to the respective
    one from the list above in the aruco_lib.py. This API's line is the only line of code you are
    allowed to modify in aruco_lib.py!!!
    
    img = cv2.imread(path_to_image)     #give the name of the image with the complete path
    id_aruco_trace = 0
    det_aruco_list = {}
    img2 = img[0:x,0:y,:]   #separate out the Aruco image from the whole image
    det_aruco_list = detect_Aruco(img2)
    if det_aruco_list:
        img3 = mark_Aruco(img2,det_aruco_list)
        id_aruco_trace = calculate_Robot_State(img3,det_aruco_list)
        print(id_aruco_trace)        
	cv2.imshow('image',img2)
	cv2.waitKey(0)
        Code for triggering color detection on ID detected 
    cv2.destroyAllWindows()
'''

yellow = [(0, 220, 220), (25, 255, 255)]
blue = [(175, 90, 50), (220, 130, 85)]
green = [(0, 160, 35), (20, 200, 75)]
red = [(0, 0, 230), (18, 18, 255)]
orange = [(40, 115, 225), (60, 135, 250)]

def color_detect(image_path, color):
    '''
    code for color Image processing to detect the color and shape of the 2 objects at max.
    mentioned in the Task_Description document. Save the resulting images with the shape
    and color detected highlighted by boundary mentioned in the Task_Description document.
    The resulting image should be saved as a jpg. The boundary should be of 25 pixels wide.
    '''
    img = cv2.imread(image_path)
    # Masking the image depending on the color
    mask = cv2.inRange(img, color[0], color[1])
    # Morphological operations on the image to refine the same
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.dilate(mask, None, iterations=2)             # Dilation
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Closing
    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        
    
    for shapes in cnts:
        shape_detection(shapes)
        

    cv2.imshow("Final_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def shape_detection(contour)
    shape = "unidentified"
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)



    M = cv2.moments(shape)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    cv2.putText(img, str(center), center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    

detect = {"Image1.jpg": [(red, "triangle"), (blue, "triangle")], 
          "Image2.jpg": [(green, "circle"), (red, "circle")],
          "Image3.jpg": [(None, None), (blue, "square")],
          "Image4.jpg": [(blue, "square"), (green, "triangle")],
          "Image5.jpg": [(blue, "circle"), (green, "square")]
         }

if __name__ == "__main__":    
    #aruco_detect(path_to_image)
    for i in detect.keys():

