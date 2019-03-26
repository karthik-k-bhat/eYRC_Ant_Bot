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
        #cv2.imshow("frame",frame)
        #cv2.waitKey(0)
        blue =[[84, 166, 114],[169, 248, 245]]
        green=[[65, 75, 49],[112, 147, 152]]
        red = [[164, 157, 68],[255, 255, 255]]
        color_range=np.array([red,green,blue])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        object_areas=list()
        for color in color_range:
                mask = cv2.inRange(hsv, color[0], color[1])
                # erode -> to remove small blobs in the image
                mask = cv2.erode(mask, kernel, iterations=1)
                # dilate -> to sharpen the edges
                mask = cv2.dilate(mask, kernel, iterations=1)
                #cv2.imshow("mask",mask)
                #cv2.waitKey(0)
                contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

                if(not contours):
                        #print("no contour for color",color)
                        object_areas.append(0)
                else:
                        object_areas.append(len(max(contours, key=len)))
        #print(object_areas)
        
        color_identified = object_areas.index(max(object_areas))
        if(max(object_areas) > 30):
            return color_identified+1
        return 0
        
#print(detect_color("align.jpg"))

def detect_sim_id(path_to_image):
    global aruco_id
    img = cv2.imread(path_to_image) #give the name of the image with the complete path
    det_aruco_list = {}
    det_aruco_list = detect_Aruco(img)  #calling detect_Aruco from the aruco library
    #print(det_aruco_list)
    if det_aruco_list:
        aruco_id = list(det_aruco_list.keys())[0] #taking only the id value
        return (aruco_id,True)
    else:
        #to start detecting the shape of the arucoId and its corresponding center
        kernel = np.ones((5, 5), np.uint8)
        color_range=np.array([[0, 0, 0], [180, 250, 100]])
        # convert the frame to HSV co-ordinates
        frame = cv2.imread(path_to_image)
        cv2.imshow("frame",frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # mask -> to apply filter to the image based on color range
        mask = cv2.inRange(hsv, color_range[0], color_range[1])
        # erode -> to remove small blobs in the image
        mask = cv2.erode(mask, kernel, iterations=1)
        # dilate -> to sharpen the edges
        mask = cv2.dilate(mask, kernel, iterations=1)
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        object = max(contours, key=len)
        # calculating the x-center and y-center
        (x, y) = ((max(object[:, :, 0])+min(object[:, :, 0]))//2, (max(object[:, :, 1])+min(object[:, :, 1]))//2) 
        #print(x,y)
        if(x<=213):
#            print("arucoid left")
            return (-1,False)
        elif(x>213 and x<416 ):
#            print("arucoid center")
            return (0,False)
        elif(x>=416):
#            print("arucoid right")
            return (1,False)
        # cv2.imshow("mask",mask)
        # cv2.waitKey(0)

#print(detect_sim_id("align.jpg"))


#for i in range(4):
#		print(i,detect_sim_id(str(i)+".png"))

def detect_trash(path_to_image):
    kernel = np.ones((5, 5), np.uint8)
    color_range=np.array([[0, 135, 135], [32, 255, 255]])
    # convert the frame to HSV co-ordinates
    frame = cv2.imread(path_to_image)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # mask -> to apply filter to the image based on color range
    mask = cv2.inRange(hsv, color_range[0], color_range[1])
    # erode -> to remove small blobs in the image
    mask = cv2.erode(mask, kernel, iterations=1)
    # dilate -> to sharpen the edges
    mask = cv2.dilate(mask, kernel, iterations=1)
    #cv2.imshow("mask",mask)
    #cv2.waitKey(0)
    # contours -> set of points which are in white
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    object = []
    if contours:
        # maximum area -> the ball
        object = max(contours, key=len)
    if(len(object)>60):
        return True
    return False

def bot_align(image,color):    #for aligning the bot after the color detection
    kernel = np.ones((5, 5), np.uint8)
    blue =[[84, 166, 114],[169, 248, 245]]
    green=[[65, 75, 49],[112, 147, 152]]
    red = [[164, 157, 68],[255, 255, 255]]
    color_range=np.array(color)
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
    if ((x-213) < 0 ):
            return -1
    elif (x-213 > 0 and x-416 <0):
            return 0
    elif (x-416>0):
            return 1