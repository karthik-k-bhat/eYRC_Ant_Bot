import numpy
import cv2
import cv2.aruco as aruco
from aruco_lib import *
import os
aruco_id = None

def detect_color(path_to_image,angle):
    # for 135 degrees  = [(150,160),(263,33),(370,155)]
    # for 45 degrees   = [(350,185),(260,75),(165,185)]
    # for 90 degrees   = [(215,285),(270,160),(430,300)]
    img = cv2.imread(path_to_image)
    cv2.imshow("img",img)
    px = list()
    ind= list()
    px.clear()
    ind.clear()
    if(angle==90):
        px.append(list(img[215,285]))
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

    for i in px:
        maxi= max(i)
        ind.append(i.index(maxi))

    if(ind.count(0)>1):
            print("BLUE")
    if(ind.count(1)>1):
            print("GREEN")
    if(ind.count(2)>1):
            print("RED")

    #print(px)
    #print(ind)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''color_dict={ "blue":[(175, 90, 50), (220, 130, 85)],
                 "green":[(0, 160, 35), (20, 200, 75)],
                 "red" : [(0, 0, 230), (18, 18, 255)]}

    col_list=list()

    img = cv2.imread(path_to_image)
    for i in color_dict.items():
        #  1. Masking the image depending on the color - makes it binary color
        mask = cv2.inRange(img,i[1][0],i[1][1])
        #       2. Morphological operations on the image to refine the same
        kernel = numpy.ones((5,5),numpy.uint8)
        mask = cv2.dilate(mask, None, iterations=2)             # Dilation
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Closing
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # To find contour in binary image
        contour = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        ctr=contour[0]
        M = cv2.moments(ctr)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        col_list.append([center,i[0]])

    col_list.sort(key= lambda x:x[0][0])
    print(col_list)
    sorted_list = list(map(lambda x: x[1],col_list))
    print(sorted_list)
    '''

def detect_sim_id(path_to_image):
    global aruco_id
    img = cv2.imread(path_to_image)     #give the name of the image with the complete path
    det_aruco_list = {}
    det_aruco_list = detect_Aruco(img)
    #print(det_aruco_list)
    if det_aruco_list:
        aruco_id = list(det_aruco_list.keys())[0]
        return aruco_id

#detect_color("1.png",45)
