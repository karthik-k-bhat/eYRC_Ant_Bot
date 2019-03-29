'''
* Team Id : 226
* Author List : Vishwas
* Filename: progress_task
* Theme: Ant Bot
* Functions: run_bot, get_sims,get_block_color move_to_node, move, turn, talk_to_arduino 
* Global Variables: serial_communication, bot_position, bot_direction, 
*                   resolution, camera, raw_capture, arena_map, immediate_node
*                   ah_list, block_list 
'''

import serial
import detection
import time
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import led

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
trash_deposit = -1
block_node_list = [[3,4,5],[6,7,8]]
number_of_nodes = 0

pick_forward = 265
block_backward = -15
ah_backward = -12
place_forward = 225
service_backward = -11

turn_flag = 0
trash_angle = 30

'''
* arena_map : This is a representation of the complete eyantra arena. The nodes
*             are numbered from 0 to 14 and the box pickup/service zones are numbered from -16 to -1.
*             Numbering of the nodes are shown in "arena.png" file presen in the "Images" folder.
*             
*             This variable is a dictionary that contains a node number and a list of 4 sets
*             as the key-value pair. Each of the 4 sets represent the directions in which other nodes
*             are present in the order North, East, South and West. An empty set represents that the
*             node does not have a path in that diresction.
'''
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

# immediate_node: contains a list of nodes that are next to each node in all directions.
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
resolution = (640, 480)                   # resolution for the frame
camera = PiCamera()                       # To initialize the PiCamera
camera.resolution = resolution            # set the resolution of the camera
camera.framerate = 30                     # Set the frame rate
rawCapture = PiRGBArray(camera, size=resolution)
camera.rotation = 90
'''
* Function Name: run_bot()
* Input: None
* Output: None
* Logic: Main function to start the bot run.
*
* Example Call: run_bot()
'''

def run_bot():

    #print("Running bot.")
    get_sims()
    for i in ant_hill_list:
        print(i)
    get_block_colours()
    #print("Blocks scanned")
    print(block_color_dict)
    print("Position",bot_position)
    print("Direction",bot_direction)
    service_list = create_all_services()
    #print("Services created.")
    for service in service_list:
        print("Executing:",service)
        execute_service(service)

    move_to_node(0)
    move(2)
    talk_to_arduino("B")

'''
* Function Name: get_block_colours()
* Input: None
* Output: None
* Logic: Go to both sides of the service areas and scan the block colors
*
* Example Call: get_block_colors()
'''

def get_block_colours():
    print("Getting block colors")
    global block_color_dict,block_node_list,camera,rawCapture
    time.sleep(1)
    move_to_node(4)
    for i in range(3):
        turn(-45)
        camera.capture("Block"+str(i+1)+".jpg")
        color = None
        rawCapture.truncate(0)
        color = detection.detect_color("Block"+str(i+1)+".jpg")
        if(color in [1,2,3]):
            led.turn_on_led(color)
            led.turn_off_led()
        block_color_dict[block_node_list[0][2-i]] = color
        print("Block color:",color)
        #print(block_node_list[0][2-i])
    turn(-45)

    move_to_node(7)
    for i in range(3):
        turn(45)
        color = None
        camera.capture("Block"+str(i+4)+".jpg")
        rawCapture.truncate(0)
        color = detection.detect_color("Block"+str(i+4)+".jpg")
        if(color in [1,2,3]):
            led.turn_on_led(color)
            led.turn_off_led()
        block_color_dict[block_node_list[1][2-i]] = color
        print("Block color:",color)
        #print(block_node_list[1][2-i])
    turn(45)

'''
* Function Name: get_sims
* Input: None
* Output: None
* Logic: Go to the central node and scan the aruco ids
*
* Example Call: get_sims()
'''
def get_sims():

    global ant_hill_list,camera,rawCapture

    move_to_node(1)
    
    for i in range(4):
        id = None
        turn(45)
        while(id is None):
            camera.capture("Sim"+str((i+1)%4)+".jpg")
            rawCapture.truncate(0)
            id,status = detection.detect_sim_id("./Sim"+str((i+1)%4)+".jpg")
            if(status == False):
                talk_to_arduino("T"+str(id*10))
                id = None
        print("ID Detected: #"+str(id))
        ant_hill = id_to_ant_hill(id)
        ant_hill_list.append(ant_hill)
        turn(45)
    turn(90)
    turn(90)
    '''
    for id in [208,99,6,33]: #[145,35,78,118]:
        ant_hill = id_to_ant_hill(id)
        ant_hill_list.append(ant_hill)
    '''

'''
* Function Name: move()
* Input: direction -> An integer from 0 to 3 denoting the direction the next node is present.
* Output:
* Logic: Calculate the turning angle, turn and then move until the next node is reached.
*
* Example Call: move(3)
'''
def move(direction):
    global bot_direction,bot_position,immediate_node

    turn_angle = get_turn_angle(direction)
    turn(turn_angle)

    #print("Current bot position:",bot_position)
    if(bot_position<0):
        bot_position = immediate_node[bot_position+16]
    else:
        bot_position = immediate_node[bot_position+16][int(bot_direction)]
    #print("Moving to position:",bot_position,"\n")
    ant_hill_nodes = [11,12,13,14]
    #if(bot_position == 2):
    #    talk_to_arduino("N")
    #    talk_to_arduino("M1")
    #    return

    if(bot_position in ant_hill_nodes):
        talk_to_arduino("N")
        talk_to_arduino("M1")
        talk_to_arduino("T90")
        talk_to_arduino("R")
        bot_direction = (bot_direction+2)%4
        talk_to_arduino("O"+str(ah_backward))
    else:
        talk_to_arduino("M1")

'''
* Function Name: turn
* Input: angle -> an integer denoting the amount of angle the bot has to turn by
* Output:
* Logic: Send the angle to the arduino and set the bot direction.
*
* Example Call: turn(90)
'''
def turn(angle):
    if(int(angle) == 0):
        return

    global bot_direction,turn_flag
    #print("Current bot direction:",bot_direction)
    bot_direction = (bot_direction + angle/90)%4
    #print("Turning to direction:",bot_direction)
    slow_turn_nodes = [3,4,5,6,7,8,10,11,12,13]
    if(angle == 90):
        if(bot_position in slow_turn_nodes):
            talk_to_arduino("D")
        else:
            talk_to_arduino("R") #Uses line sensing and hence more efficient.
    elif angle == -90:
        if(bot_position in slow_turn_nodes):
            talk_to_arduino("A")
        else:
            talk_to_arduino("L")
    elif (angle == 45 or angle == -45):
        if(turn_flag):
            if(angle == 45):
                talk_to_arduino("R")
            else:
                talk_to_arduino("L")
        else:
            talk_to_arduino("T"+str(angle))
        turn_flag = (turn_flag+1)%2
    else:
        talk_to_arduino("T"+str(angle))

'''
* Function Name: move_to_node
* Input: node -> an integer denoting the node the bot has to move to
* Output:
* Logic: move the bot from node to node iteratively using the arena_map and immediate_node dictionaries.
*
* Example Call: move_to_node(10)
'''
def move_to_node(node):
    global bot_position, arena_map

    if(node is None):
        print("Can't move to None node.")
        return

    while bot_position != node:
        if(bot_position<0):
            move(arena_map[bot_position])
        else:
            for i in range(4):
                if node in arena_map[bot_position][i]:
                    move(i)
                    break

'''
* Function Name: get_turn_angle
* Input: direction -> Integer between 0 to 4 denoting the direction
* Output: turn_angle -> Positive or negative integer denoting the angle and direction of the turn
* Logic: Find the minimum angle required to reach the direction.
*
* Example Call: get_turn_angle(1)
'''
def get_turn_angle(direction):
    global bot_direction

    if((bot_direction-direction)%4 < (direction-bot_direction)%4):
        return -90*((bot_direction-direction)%4)
    else:
        return 90*((direction-bot_direction)%4)

'''
* Function Name: id_to_ant_hill
* Input: id -> An interger detected from the SIMs
* Output: ant_hill -> A dictionary having the ant hill information
* Logic: Convert the integer id to a binary string and extract the required information.
*
* Example Call: id_to_an_hill(7)
'''

def id_to_ant_hill(id):
    ant_hill = {'ah_number':None, 'is_qah':None, 'service_1':None, 'service_2':None, "trash":None}
    binary_string = bin(id)[2:]
    binary_string = '0'*(8-len(binary_string)) + binary_string #To add preceding zeros
    ant_hill['is_qah'] = int(binary_string[0],2)
    ant_hill['ah_number'] = int(binary_string[1:3],2)
    ant_hill['service_2'] = int(binary_string[3:5],2)
    ant_hill['service_1']  = int(binary_string[5:7],2)
    ant_hill['trash'] = int(binary_string[7])
    return ant_hill

def create_all_services():
    global ant_hill_list
    block_services = []
    trash_services = []
    final_services = []

    print("Starting")

    for ant_hill in ant_hill_list:
        ant_hill_node = ant_hill['ah_number']+11
        services = []
        if(ant_hill['service_1']):
            services.append((ant_hill_node,0,1,ant_hill['service_1']))
        if(ant_hill['service_2']):
            services.append((ant_hill_node,0,2,ant_hill['service_2']))
        if(ant_hill['trash']):
            trash = None
            if(ant_hill['service_1']):
                trash = 2
            elif(ant_hill['service_2']):
                trash = 1
            services.append((ant_hill_node,1,trash,None))

        if(ant_hill['is_qah']):
            final_services.extend(services)
        else:
            for service in services:
                if(service[1] == 1):
                    trash_services.append(service)
                else:
                    block_services.append(service)

    #print("Optimising")

    while(block_services and trash_services):
        if(not final_services or final_services[-1][1] == 1):
            service = block_services.pop()
            final_services.append(service)
        else:
            last_service = final_services[-1]
            flag1 = 1
            for service in trash_services:
                if(service[0] == last_service[0]):
                    trash_services.remove(service)
                    final_services.append(service)
                    flag1 = 0
                    break
            if(flag1):
                present_node = final_services[-1][0]
                opposite_nodes_list = [[11,14],[12,13]]
                for nodes in opposite_nodes_list:
                    if(present_node in nodes):
                        opposite_node = sum(nodes) - present_node
                flag2 = 1
                for service in block_services:
                    if(service[0] == opposite_node):
                        flag2 = 0
                        break
                if(flag2):
                    for service in trash_services:
                        if(service[0] == opposite_node):
                            trash_services.remove(service)
                            final_services.append(service)
            if(last_service == final_services[-1]):
                service = block_services.pop()
                final_services.append(service)

    final_services.extend(block_services)
    final_services.extend(trash_services)

    return final_services

def execute_service(service):
    global camera,rawCapture

    if(service[1]):
        print("Current direction:",bot_direction)
        move_to_node(service[0])
        if(service[2] == 1):
            pick_place('Right')
        elif(service[2] == 2):
            pick_place('Left')
        else:
            pick_place('Check')
        deposit_trash()

    else:
        block_node = None
        flag = 0
        nodes_list = zip(*block_node_list)
        for nodes in nodes_list:
            for node in nodes[::-1]:
                if(block_color_dict[node] == service[3]):
                    block_node = node
                    flag = 1
                    break
            if(flag):
                break
        block_color_dict[block_node] = 0

        move_to_node(block_node)
        angle = get_turn_angle(2)
        turn(angle)

#        camera.capture("align.jpg")
#        rawCapture.truncate(0)
#        angle = detection.bot_align("align.jpg",service[3])
#        print("Align:",angle)
#        if(angle != 0):
#            talk_to_arduino("T"+str(angle*10))
        talk_to_arduino("P1")
        talk_to_arduino('S'+str(pick_forward))
        talk_to_arduino('P2')
        talk_to_arduino('O'+str(block_backward))

        move_to_node(service[0])
        if(service[2] == 1):
            pick_place('Right')
        else:
            pick_place('Left')


def pick_place(status):

    global camera,rawCapture
    direction = 0

    if(status == 'Check'):
        turn(90)
        camera.capture("Trash.jpg")
        rawCapture.truncate(0)

        result = detection.detect_trash("Trash.jpg")

        if(result):
            led.turn_on_led(4)
            led.turn_off_led
            talk_to_arduino("P1")
            talk_to_arduino('S'+str(pick_forward))
            talk_to_arduino('P2')
            talk_to_arduino('O'+str(service_backward))
            turn(-90)
        else:
            turn(-90)
            turn(-90)
            led.turn_on_led(4)
            led.turn_off_led()
            talk_to_arduino("P1")
            talk_to_arduino('S'+str(pick_forward))
            talk_to_arduino('P2')
            talk_to_arduino('O'+str(service_backward))
        return

    if(status == 'Right'):
        direction = 1
    elif(status == 'Left'):
        direction = -1

    turn(direction*90)
    talk_to_arduino('S'+str(place_forward))
    talk_to_arduino('P3')
    talk_to_arduino('O'+str(service_backward))
    turn(direction*90*-1)

def deposit_trash():
    global trash_deposit,bot_direction

    move_to_node(2)
    turn(trash_deposit*30)
    talk_to_arduino('P3')
    turn(-1*trash_deposit*30)
    talk_to_arduino('O-30')
    turn(90)
    bot_direction = (bot_direction+1)%4
    trash_deposit *= -1

'''
* Function Name : talk_to_arduino
* Input         : action -> Message that has to be sent to arduino
* Output        : None
* Logic         : a) Sends the message to arduino and waits for a job done signal.
*                 b) Optimises multiple "M" commands for faster bot movement.
*
* Example Call: talk_to_arduino("M1")
'''
def talk_to_arduino(action):

    global serial_communication,number_of_nodes
    
    # This part of the code is to add up all the consecutive "M1" commands and send them at once.
    # It increases the efficiency of line follower.
#    if(action == "M1"):
#        number_of_nodes += 1
#        return
#    else:
#        if(number_of_nodes):
#            print("M:",number_of_nodes)
#            serial_communication.write(("M"+str(number_of_nodes)).encode())
#            while(1):
#                if(serial_communication.in_waiting>0):
#                    response = serial_communication.readline().decode().strip("\n").strip("\r")
#                    if response == "Job done":
#                        break
#                    else:
#                       print(response)
#            number_of_nodes = 0
    
    print("Talking to arduino:",action)
    # Send the encoded signal to Arduino through serial communication
    serial_communication.write(action.encode())
    # Wait until a 'Job done' signal is returned.
    # This helps while taking pictures and scanning Sims and Blocks.
    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline().decode().strip("\n").strip("\r")
            if response == "Job done":
                break
            else:
                print(response)

def service_check():
    #Go to corner node
    talk_to_arduino("M1")
    talk_to_arduino("M1")
    talk_to_arduino("R")
    talk_to_arduino("M1")
    talk_to_arduino("M1")
    talk_to_arduino("M1")
    talk_to_arduino("R")

    #Pick and go to node 0
    talk_to_arduino("P1")
    talk_to_arduino("O"+str(pick_forward))
    time.sleep(1)
    talk_to_arduino("P2")
    talk_to_arduino("O"+str(service_backward))
    time.sleep(1)
    talk_to_arduino("R")
    talk_to_arduino("M1")
    talk_to_arduino("M1")
    talk_to_arduino("M1")
    talk_to_arduino("R")

    #Go to a corner service place
    talk_to_arduino("M1")
    talk_to_arduino("R")
    talk_to_arduino("M1")
    talk_to_arduino("R")
    talk_to_arduino("N")
    talk_to_arduino("M1")

    #Turn and place block

    talk_to_arduino("T90")
    talk_to_arduino("R")
    talk_to_arduino("O"+str(ah_backward))
    time.sleep(1)
    talk_to_arduino("R")
    talk_to_arduino("O"+str(service_forward))
    time.sleep(1)
    talk_to_arduino("P3")
    talk_to_arduino("O"+str(service_backward))
    time.sleep(1)
    talk_to_arduino("L")

def trash_check():
    #Go front and pick trash
    talk_to_arduino("M1")
    talk_to_arduino("N")
    talk_to_arduino("M1")
    talk_to_arduino("T90")
    talk_to_arduino("R")
    talk_to_arduino("O"+str(ah_backward))
    talk_to_arduino("L")
    talk_to_arduino("P1")
    talk_to_arduino("O"+str(service_forward))
    talk_to_arduino("P2")
    talk_to_arduino("O"+str(service_backward))
    talk_to_arduino("R")

    #Go to trash_zone and place
    talk_to_arduino("M1")
    talk_to_arduino("R")
    talk_to_arduino("M1")
    talk_to_arduino("R")
    talk_to_arduino("M1")
    talk_to_arduino("T"+str(trash_angle))
    talk_to_arduino("P3")
    talk_to_arduino("T-"+str(trash_angle))
    talk_to_arduino("O-20")
    talk_to_arduino("R")
    talk_to_arduino("M1")
    talk_to_arduino("M1")

if __name__ == "__main__":
    camera.start_preview()
    time.sleep(2)      # Wait for arduino to initialise
    led.turn_off_led() # Turn off led before beginning the run
    talk_to_arduino("M1")
    run_bot()          # Main function that runs the bot
    #service_check()
    #trash_check()
    led.end_led()      # Stop led after the run
    camera.stop_preview()
