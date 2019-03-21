import numpy
import cv2
import cv2.aruco as aruco
from aruco_lib import *
import os
aruco_id = None
"""
def detect_color(path_to_image,angle):  # color detection function
    # taking 3 points from the image to get its bgr values
    # for 135 degrees  = [(150,160),(263,33),(370,155)]
    # for 45 degrees   = [(350,185),(260,75),(165,185)]
    # for 90 degrees   = [(215,285),(270,160),(430,300)]
    img = cv2.imread(path_to_image)
    px = list()
    ind= list()
    px.clear()
    ind.clear()
    if(angle==-7 or angle==-2):
        for i in range(60,350):
            for j in range(0,310):
                px.append(list(img[j,i]))   #getting bgr values of that pixel and adding to list
    if(angle==-3 or angle==-6):
        for i in range(140,480):
            for j in range(212,470):
                px.append(list(img[j,i]))
        
    if(angle==-4 or angle==-5):
        for i in range(300,610):
            for j in range(2,310):
                px.append(list(img[j,i]))

    for i in px:        # looping through the rgb values list of 3 points in the image
        maxi= max(i)

        ind.append(i.index(maxi))   #getting the index of the max value in rgb

    if(ind.count(0)>42000):     #counting the no of Blue Green or Red value
            return "BLUE"
    if(ind.count(1)>42000):     #if one color found two or more times , print that color
            return "GREEN"
    if(ind.count(2)>42000):
            return "RED"

    #print(px)
    #print(ind)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
"""
def detect_color(path_to_image):
        frame = cv2.imread(path_to_image)
        kernel = np.ones((5, 5), np.uint8)

        blue =[[84, 166, 114],[169, 248, 245]]
        green=[[65, 75, 49],[112, 147, 152]]
        red = [[164, 157, 68],[255, 255, 255]]
        color_range=np.array([blue,green,red])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, color_range[0][0], color_range[0][1])
        # erode -> to remove small blobs in the image
        mask = cv2.erode(mask, kernel, iterations=1)
        # dilate -> to sharpen the edges
        mask = cv2.dilate(mask, kernel, iterations=1)
        cv2.imshow("mask",mask)
        cv2.waitKey(0)
detect_color("blue.jpg")

def detect_sim_id(path_to_image):
    global aruco_id
    img = cv2.imread(path_to_image) #give the name of the image with the complete path
    det_aruco_list = {}
    det_aruco_list = detect_Aruco(img)  #calling detect_Aruco from the aruco library
    #print(det_aruco_list)
    if det_aruco_list:
        aruco_id = list(det_aruco_list.keys())[0] #taking only the id value
        return aruco_id
        
#for i in range(4):
#		print(i,detect_sim_id(str(i)+".png"))

def detect_trash(path_to_image):
        img= cv2.imread(path_to_image)
        px = list()
        count=0
        px.clear()
                             
        px.append(list(img[184,110]))   #getting bgr values of that pixel and adding to list px
        px.append(list(img[340,52]))
        px.append(list(img[430,160]))
        px.append(list(img[297,207]))
        #print(px)
        for i in px:
                if((i[0]-i[2])>60 and (i[1]-i[2])>60):
                        count=count+1
        if(count>2):
                return True
        else:
                return False

def bot_align(image):    #for aligning the bot after the color detection
    kernel = np.ones((5, 5), np.uint8)
    color_range=np.array([[0, 135, 135], [32, 255, 255]])
    # convert the frame to HSV co-ordinates
    frame = cv2.imread(image)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # mask -> to apply filter to the image based on color range
    mask = cv2.inRange(hsv, color_range[0], color_range[1])
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
    return (cv.contourArea(cnt))
print(bot_align("trash.jpg"))