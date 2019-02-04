'''
* Team Id          : 226
* Author List      : Vishwas
* Filename         : progress_task
* Theme            : Ant Bot
* Functions        : get_sims, talk_to_arduino, pick_block 
* Global Variables : serial_communication, resolution, camera, raw_capture, aruco_id_list
'''

# Import packages
import serial
import detection
import time
import csv
from picamera import PiCamera 
from picamera.array import PiRGBArray

# Initialise serial communication between Pi and Arduino
serial_communication = serial.Serial('/dev/ttyUSB0',9600)

# Setup the PiCamera
resolution = (608, 368)         # resolution for the frame
camera = PiCamera()             # To initialize the PiCamera
camera.resolution = resolution  # set the resolution of the camera
camera.framerate = 16           # Set the frame rate
raw_capture = PiRGBArray(camera, size=resolution)

aruco_id_list = []

'''
* Function Name : get_sims
* Input         : None
* Output        : None
* Logic         : Moves from the start position to the central node and detects the Arcuo Ids (Sims)
*                 Save the IDs in the global variable 'aruco_id_list'
* Example Call  : get_sims()
'''
def get_sims():

    global aruco_id_list

    # Wait for line sensor calibration
    time.sleep(8)

    # Move to central node  
    talk_to_arduino("M1")   # 'M1' makes the bot move forward till it endcounters a node 
    time.sleep(3)           # Wait for bot to each the node
    talk_to_arduino("M1")
    time.sleep(5)
    talk_to_arduino("O")    # 'O' makes the bot move a hard-coded distance of 10cm.
    time.sleep(3)
    
    #Open the pick/place mechanism and set the PiCamera to the right angle
		talk_to_arduino("C")
		time.sleep(1)
		
    #Turn towards each sim and capture the images.
    talk_to_arduino("T45")  # 'TX' makes the robot turn by X degress
    time.sleep(2)
    camera.capture("1.png") # Captures an image and saves it with the input as file name

    talk_to_arduino("T90")
    time.sleep(2)
    camera.capture("2.png")

    talk_to_arduino("T90")
    time.sleep(2)
    camera.capture("3.png")

    talk_to_arduino("T90")
    time.sleep(2)
    camera.capture("0.png")

    talk_to_arduino("T45")

    # Detect sim id from the captured images
    for file_name in range(4):
        id = detection.detect_sim_id("./"+str(file_name)+".png")
        aruco_id_list.append(id)

    # Create csv file
    file_name = "eYRC#AB#226.csv"
    with open(file_name,'w') as file:
        writer = csv.writer(file)
        
        # Write the detected IDs
        for sim_number in range(4):
            row = ['SIM '+str(sim_number), str(aruco_id_list[sim_number])]
            writer.writerow(row)


'''
* Function Name : pick_block
* Input         : None
* Output        : None
* Logic         : Moves towards the block, picks it up and places it back again.
* Example Call  : pick_block()
'''
def pick_block():
    
    time.sleep(1)
    # Move the bot forward by 10cm 
    talk_to_arduino("O")
    time.sleep(1)

    #Pick the box and place it back
    talk_to_arduino("P")  # 'P' alternates between pick and place.
    time.sleep(1)

    talk_to_arduino("P")
    
'''
* Function Name : talk_to_arduino
* Input         : action -> String that denotes the action that has to be performed by the bot.
* Output        : None
* Logic         : Encodes the action and sends the message to arduino using serial communication.
* Example Call  : talk_to_arduino("M1")
'''
def talk_to_arduino(action):
    global serial_communication

    message = action.encode()           # Encode the string
    serial_communication.write(message)

if __name__ == "__main__":

    # Run the bot to detect the Aruco IDs (Task A) 
    get_sims()

    # Run the bot to pick a block (Task B)
    # pick_block()

