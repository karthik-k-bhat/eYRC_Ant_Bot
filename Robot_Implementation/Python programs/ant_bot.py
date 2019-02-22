#Last edited: 16 Feb 2019
#Edited By: Vishwas N S
#Last edit details: 

import serial
import detection
import time
from picamera import PiCamera
from picamera.array import PiRGBArray

# Initialising Globals

# Directions
NORTH = 0
NORTH_EAST = 0.5
EAST = 1
SOUTH_EAST = 1.5
SOUTH = 2
SOUTH_WEST = 2.5
WEST = 3
NORTH_WEST = 3.5

# Bot
serial_communication = serial.Serial('/dev/ttyUSB0',9600)
bot_position = -1
bot_direction = NORTH
ant_hill_list = []
block_color_dict = {}

# Map
arena_map = {
    -16: SOUTH,-15: EAST,-14: WEST,-13: EAST,-12: WEST,-11: WEST,-10: EAST,-9: WEST,-8: EAST,-7: NORTH,-6: NORTH,-5: NORTH,-4: NORTH,-3: NORTH,-2: NORTH,-1: NORTH,
        0: [{-16,-15,-14,-13,-12,-11,-10,-9,-8,1,2,9,10,11,12,13,14},{-7,-6,-5,6,7,8},{-1},{-4,-3,-2,3,4,5}],
        1: [{-16,2},{-13,-12,-11,-10,12,13},{-7,-6,-5,-4,-3,-2,-1,0,3,4,5,6,7,8},{-15,-14,-9,-8,9,11,14}],
        2: [{-16},set(),{-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,3,4,5,6,7,8,9,10,11,12,13,14},set()],
        3: [set(),{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-1,0,1,2,6,7,8,9,10,11,12,13,14},{-2},{-4,-3,4,5}],
        4: [set(),{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-2,-1,0,1,2,3,6,7,8,9,10,11,12,13,14},{-3},{-4,5}],
        5: [set(),{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-3,-2,-1,0,1,2,3,4,6,7,8,9,10,11,12,13,14},{-4},set()],
        6: [set(),{-7,-6,7,8},{-5},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-4,-3,-2,-1,0,1,2,3,4,5,9,10,11,12,13,14}],
        7: [set(),{-7,8},{-6},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,9,10,11,12,13,14}],
        8: [set(),set(),{-7},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,9,10,11,12,13,14}],
        9: [{-9,-8,11},{-16,-13,-12,-11,-10,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,10,12,13},{-15,-14,14},set()],
        10: [{-11,-10,12},set(),{-13,-12,13},{-16,-15,-14,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,11,14}],
        11: [set(),{-9},{-16,-15,-14,-13,-12,-11,-10,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,12,13,14},{-8}],
        12: [set(),{-11},{-16,-15,-14,-13,-12,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,13,14},{-10}],
        13: [{-16,-15,-14,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,14},{-12},set(),{-13}],
        14: [{-16,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13},{-14},set(),{-15}],
}

immediate_node = [
    2,14,14,13,13,12,12,11,11,8,7,6,5,4,3,0,
    [1,6,-1,3],
    [2,10,0,9],
    [-16,None,1,None],
    [None,0,-1,4],
    [None,3,-3,5],
    [None,4,-4,None],
    [None,7,-5,0],
    [None,8,-6,6],
    [None,None,-7,7],
    [11,1,14,None],
    [12,None,13,1],
    [None,-9,9,-8],
    [None,-11,10,-10],
    [10,-13,None,-12],
    [9,-15,None,-14],
]

# Camera
resolution = (608, 368)                   # resolution for the frame
camera = PiCamera()                       # To initialize the PiCamera
camera.resolution = resolution            # set the resolution of the camera
camera.framerate = 16                     # Set the frame rate
rawCapture = PiRGBArray(camera, size=res) 

def run_bot():
    print("Running bot.")
    get_block_colours()
    print("Blocks scanned")
    get_sims()
    print("Sims scanned")

    for ant_hill in ant_hill_list:
        if(ant_hill['is_qah']):
            print("QAH id:",ant_hill['ah_number'])
            service(ant_hill)
            print("Serviced QAH")
            ant_hill_list.remove(ant_hill)
            break

    for ant_hill in ant_hill_list:
        service(ant_hill)
        print("Serviced AH")

def get_block_colours():
    
    global block_color_dict,camera,rawCapture
    color_code = {"Red":1,"Green":2,"Blue":3}
    move_to_node(4)
    node_list = [-4,-3,-2]
    for _ in range(3):
        turn(-45)
        camera.capture("Block"+str(i+1)+".jpg")
        rawCapture.truncate(0)
        colour = detection.detect_color("Block"+str(i+1)+".jpg",45)
        block_color_dict[node_list[i]] = colour
        print("Shrub node:",node_list[i])
        print("Color:",color)
    turn(-45)

    move_to_node(7)
    node_list = [-7,-6,-5]
    for _ in range(3):
        turn(45)
        camera.capture("Block"+str(i+4)+".jpg")
        rawCapture.truncate(0)
        colour = detection.detect_color("Block"+str(i+4)+".jpg",45)
        block_color_dict[node_list[i]] = colour
    turn(45)

def get_sims():
    
    global ant_hill_list,camera,rawCapture

    move_to_node(1)
    turn(-45)
    for i in range(4):
        camera.capture("Sim"+str(i)+".jpg")
        rawCapture.truncate(0)
        id = detection.detect_sim_id("./Sim"+str(i*2)+".jpg")
        ant_hill = id_to_ant_hill(id)
        ant_hill_list.append(ant_hill)
        turn(90)

    turn(45)

def move(direction, distance = 0):

    global bot_direction,bot_position
    talk_to_arduino("O11")

    turn_angle = get_turn_angle(direction)
    turn(turn_angle)
    
    position = immediate_node[bot_position][direction]
    if(distance == 0):
        talk_to_arduino("M1")
    else:
        talk_to_arduino("O"+str())

def turn(angle):
    global bot_direction

    bot_direction = (bot_direction + angle/90)%4
    talk_to_arduino("T",str(angle))

def move_to_node(node):
    global bot_position, arena_map

    while bot_position != node:
        if(bot_position<0):
            move(arena_map[bot_position])
        else:
            for i in range(4):
                if node in arena_map[bot_position][i]:
                    move(i)
                    break

def get_turn_angle(direction):
    global bot_direction

    turn_angle = min(abs(direction - bot_direction),abs(direction-bot_direction+4))*90
    sign = -1 if bot_direction+2<direction else 1
    return turn_angle*sign

def service(ant_hill):
    service_1_node = (-2*ant_hill['ah_number'])-8
    service_2_node = (-2*ant_hill['ah_number'])-9
    ant_hill_node = ant_hill['ah_number']+11

    if(ant_hill['trash']):
        move_to_node(ant_hill_node)
        trash_node = None
        if(ant_hill['service_1']):
            trash_node = service_2_node
        elif(ant_hill['service_2']):
            trash_node = service_1_node
        else:
            move_to_node(service_1_node)
            camera.capture("Trash.jpg")
            rawCapture.truncate(0)
            result = detection.detect_color("Trash.jpg",45)
            if(result == True):
                trash_node = service_1_node
            else:
                trash_node = service_2_node

        move_to_node(trash_node)
        talk_to_arduino("P")
        move_to_node(-16)
        if(first_trash_deposited):
            turn_angle = 22
        else:
            turn_angle = -22
        turn(turn_angle)
        talk_to_arduino("P")
        turn(turn_angle)

    block_node = None

    if(ant_hill['service_1']):
        for node in block_color_dict:
            if(block_color_dict[node]==ant_hill['service_1']):
                block_node = node
                node = None
                move_to_node(block_node)
                talk_to_arduino("P")
                move_to_node(service_1_node)
                talk_to_arduino("P")
                break

    if(ant_hill['service_2']):
        for node in block_color_dict:
            if(block_color_dict[node]==ant_hill['service_2']):
                block_node = node
                node = None
                move_to_node(block_node)
                talk_to_arduino("P")
                move_to_node(service_2_node)
                talk_to_arduino("P")
                break

def id_to_ant_hill(id):
    ant_hill = {'ah_number':None, 'is_qah':None, 'service_1':None, 'service_2':None, "trash":None}
    binary_string = bin(id)
    binary_string = '0'*(8-len(self.binary_string)) + self.binary_string #To add preceding zeros
    ant_hill['is_qah'] = int(binary_string[0],2)
    ant_hill['ah_number'] = int(self.binary_string[1,3],2)
    ant_hill['service_2'] = int(self.binary_string[3,5],2)
    ant_hill['service_1']  = int(self.binary_string[5,7],2)
    ant_hill['trash'] = int(self.binary_string[7])
    return ant_hill

def talk_to_arduino(action, value=None):
    global serial_communication

    serial_communication.write(action.encode())
    
    if(value is not None):
        serial_communication.write(value.encode())

    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline().decode().strip("\n").strip("\r")
        if response == "1":
            break
        else:
            print(response)
        time.sleep(1)

if __name__ == "__main__":
    run_bot()
