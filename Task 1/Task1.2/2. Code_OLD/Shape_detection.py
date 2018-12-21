import numpy as np
import cv2
import cv2.aruco as aruco

yellow = [(0, 220, 220), (25, 255, 255)]
blue = [(175, 90, 50), (220, 130, 85)]
green = [(0, 160, 35), (20, 200, 75)]
red = [(0, 0, 230), (18, 18, 255)]
orange = [(40, 115, 225), (60, 135, 250)]

contour_color = {red[0] : green[0], green[0] : blue[0], blue[0] : red[0]}

image_dict = {"Image1.jpg" : [(red, "triangle"), (blue, "triangle")], 
              "Image2.jpg" : [(green, "circle"), (red, "circle")],
              "Image3.jpg" : [(None, None), (blue, "square")],
              "Image4.jpg" : [(blue, "square"), (green, "triangle")],
              "Image5.jpg" : [(blue, "circle"), (green, "square")]
             }

aruco_4x4_100 = aruco.Dictionary_get(aruco.DICT_4X4_100)
aruco_5x5_1000 = aruco.Dictionary_get(aruco.DICT_5X5_1000)
aruco_7x7_250 = aruco.Dictionary_get(aruco.DICT_7X7_250)
aruco_info = {"Image1.jpg": [aruco_4x4_100], "Image2.jpg": [aruco_4x4_100],
              "Image3.jpg": [aruco_5x5_1000], "Image4.jpg": [aruco_5x5_1000], "Image5.jpg": [aruco_7x7_250]}

identified_shapes = dict()
for image in image_dict.keys():
    identified_shapes[image] = list()

def color_detect(image_path, shape_details):
    color = shape_details[0]
    img = cv2.imread(image_path)
    # Masking the image depending on the color
    mask = cv2.inRange(img, color[0], color[1])
    # Morphological operations on the image to refine the same
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.dilate(mask, None, iterations=2)             # Dilation
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Closing
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contour = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None    
    for unidentified_shape in contour:
        detect_shape(image_path, unidentified_shape, shape_details)

    
def detect_shape(image_name, contour, shape_details):
    color = shape_details[0]
    shape = shape_details[1]
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
    
    M = cv2.moments(contour)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    if len(approx) == 3 and shape == "triangle":
        identified_shapes[image_name].append(("triangle", color, center, contour))
    elif len(approx) == 4 and shape == "square":
        identified_shapes[image_name].append(("square", color, center, contour))
    elif len(approx) > 4:
        x_len = int(max(contour[:, :, 0]) - min(contour[:, :, 0]))
        y_len = int(max(contour[:, :, 1]) - min(contour[:, :, 1]))
        if (x_len > 1.2 * y_len) and shape == "ellipse":
            identified_shape[image_name].append(("ellipse", color, center, contour))
        elif shape == "circle": 
            identified_shapes[image_name].append(("circle", color, center, contour))


def detect_Aruco(image, aruco_dict):  #returns the detected aruco list dictionary with id: corners
    aruco_list = {}
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    parameters = aruco.DetectorParameters_create()
    corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters = parameters)
    gray = aruco.drawDetectedMarkers(gray, corners,ids)
    if len(corners):
        for k in range(len(corners)):
            temp_1 = corners[k]
            temp_1 = temp_1[0]
            temp_2 = ids[k]
            temp_2 = temp_2[0]
            aruco_list[temp_2] = temp_1
        aruco_info[image].append(int(temp_2))
        return aruco_list


def mark_Aruco(img, aruco_list):
    key_list = aruco_list.keys()
    font = cv2.FONT_HERSHEY_SIMPLEX
    for key in key_list:
        dict_entry = aruco_list[key]
        centre = dict_entry[0] + dict_entry[1] + dict_entry[2] + dict_entry[3]
        centre[:] = [int(x / 4) for x in centre]
        orient_centre = centre + [0.0,5.0]
        centre = tuple(centre)  
        orient_centre = tuple((dict_entry[0]+dict_entry[1])/2)
        cv2.circle(img,centre,1,(0,0,255),8)
        cv2.circle(img,tuple(dict_entry[0]),1,(0,0,255),8)
        cv2.circle(img,tuple(dict_entry[1]),1,(0,255,0),8)
        cv2.circle(img,tuple(dict_entry[2]),1,(255,0,0),8)
        cv2.circle(img,orient_centre,1,(0,0,255),8)
        cv2.line(img,centre,orient_centre,(255,0,0),4)
        cv2.putText(img, str(key), (int(centre[0] + 20), int(centre[1])), font, 1, (0,0,255), 2, cv2.LINE_AA)


if __name__ == "__main__":   
    fo = open("226_Task1.2.csv", "w+")
    fo.write("Image Name"+","+"ArUco ID"+","+"(x-y) Object-1"+","+"(x-y) Object-2") 
    for i in range(1,6):
        fo.write("\n")
        image = "Image" + str(i) + ".jpg"; 
        fo.write(str(image)+",")

        # ARUCO ID TO BE AVAILABLE HERE TO WRITE TO CSV FILE
        aruco_list = detect_Aruco(image, aruco_info[image][0])
        fo.write(str(aruco_info[image][1])+",")
        result_image = cv2.imread(image)

        for data in image_dict[image]:
            if (data[0]) != None:
                color_detect(image, data)
            else:
                identified_shapes[image].append((None, None, None, None))

        for shapes in identified_shapes[image]:
            if shapes[0] != None:
                centroid = shapes[2]
                cv2.drawContours(result_image, [shapes[3]], -1, contour_color[shapes[1][0]], 25)
                cv2.putText(result_image, str(centroid), centroid, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                fo.write(str(centroid).replace(',','-'))
                fo.write(",")
            else:
                fo.write("(None- None)" + ",")
        
        mark_Aruco(result_image, aruco_list)

        cv2.imwrite("Result_"+image,result_image)
    fo.close()