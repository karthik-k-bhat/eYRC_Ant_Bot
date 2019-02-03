import numpy
import cv2
import cv2.aruco as aruco
from aruco_lib import *
import os
aruco_id = None

def detect_color(path_to_image,angle):  # color detection function
    # taking 3 points from the image to get its bgr values
    # for 135 degrees  = [(150,160),(263,33),(370,155)]
    # for 45 degrees   = [(350,185),(260,75),(165,185)]
    # for 90 degrees   = [(215,285),(270,160),(430,300)]
    img = cv2.imread(path_to_image)    #reading image
    cv2.imshow("img",img)
    px = list()
    ind= list()
    px.clear()
    ind.clear()
    if(angle==90):                      
        px.append(list(img[215,285]))   #getting bgr values of that pixel and adding to list px
        px.append(list(img[270,160]))
        px.append(list(img[430,300]))

    if(angle==45):
        px.append(list(img[350,185]))
        px.append(list(img[260,75]))
        px.append(list(img[165,185]))

    if(angle==135):
        px.append(list(img[150,160]))
        px.append(list(img[263,33]))
        px.append(list(img[370,155]))

    for i in px:        # looping through the rgb values list of 3 points in the image
        maxi= max(i)
        ind.append(i.index(maxi))   #getting the index of the max value in rgb

    if(ind.count(0)>1):     #counting the no of Blue Green or Red value  
            print("BLUE")
            return "BLUE"
    if(ind.count(1)>1):     #if one color found two or more times , print that color
            print("GREEN")
            print "GREEN"
    if(ind.count(2)>1):
            print("RED")
            return "RED"

    #print(px)
    #print(ind)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()

def detect_sim_id(path_to_image):
    global aruco_id
    img = cv2.imread(path_to_image)     #give the name of the image with the complete path
    det_aruco_list = {}
    det_aruco_list = detect_Aruco(img)  #calling detect_Aruco from the aruco library
    #print(det_aruco_list)
    if det_aruco_list:
        aruco_id = list(det_aruco_list.keys())[0] #taking only the id value
        return aruco_id

#detect_color("1.png",45)
