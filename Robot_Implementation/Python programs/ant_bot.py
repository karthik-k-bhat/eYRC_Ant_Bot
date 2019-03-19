'''
* Team Id : 226
* Author List : Vishwas, 
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
camera.framerate = 16                     # Set the frame rate
rawCapture = PiRGBArray(camera, size=resolution) 

'''
* Function Name: run_bot()
* Input: None
* Output: None
* Logic: Main function to start the bot run.
*
* Example Call: run_bot()
'''

def run_bot():

    print("Running bot.")
    get_block_colours()
    print("Blocks scanned")
    get_sims()

    service_list = create_all_services()
    
    for service in service_list:
        execute_service(servie)
 '''       
    for ant_hill in ant_hill_list:
        if(ant_hill['is_qah']):
            #print("QAH id:",ant_hill['ah_number'])
            service(ant_hill)
            #print("Serviced QAH")
            ant_hill_list.remove(ant_hill)
            break

    for ant_hill in ant_hill_list:
        service(ant_hill)
        #print("Serviced AH")
'''

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
    global block_color_dict,camera,rawCapture
    camera.start_preview()
    
    move_to_node(4)
    node_list = [-4,-3,-2]
    for i in range(3):
        turn(-45)
        camera.capture("Block"+str(i+1)+".jpg")

        rawCapture.truncate(0)
        color = detection.detect_color("Block"+str(i+1)+".jpg",45)
        block_color_dict[node_list[i]] = color
        print("Block color:",color)
    turn(-45)

    move_to_node(7)
    node_list = [-7,-6,-5]
    for i in range(3):
        turn(45)
        camera.capture("Block"+str(i+4)+".jpg")
        rawCapture.truncate(0)
        colour = detection.detect_color("Block"+str(i+4)+".jpg",45)
        block_color_dict[node_list[i]] = color
        print("Block color:",color)
    turn(45)
    camera.stop_preview()

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
    camera.start_preview()
    for i in range(4):
        turn(45)
        camera.capture("Sim"+str((i+1)%4)+".jpg")
        rawCapture.truncate(0)
        id = detection.detect_sim_id("./Sim"+str((i+1)%4)+".jpg")
        print("ID Detected:",id)
        ant_hill = id_to_ant_hill(id)
        ant_hill_list.append(ant_hill)
        turn(45)
    camera.stop_preview()

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
    if(bot_position in ant_hill_nodes):
        talk_to_arduino("N")
        talk_to_arduino("M1")
        turn(180)
        talk_to_arduino("O-10")
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
    if(angle == 90):
        talk_to_arduino("R") #Uses line sensing and hence more efficient.    
    elif angle == -90:
        talk_to_arduino("L")
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

    turn_angle = min((bot_direction-direction)%4,(direction-bot_direction)%4)*90
    sign = -1 if bot_direction+2<direction else 1
    return turn_angle*sign

'''
* Function Name: service
* Input: ant_hill -> A dictionary containing the details of the ant_hill that has to be serviced
* Output:
* Logic: Checks the ant_hill for service requirements and provides them if required.
*        Later checks for the trash and picks it up if present.
*
* Example Call: service(ant_hill)
'''

def service(ant_hill):
    service_1_node = (-2*ant_hill['ah_number'])-8
    service_2_node = (-2*ant_hill['ah_number'])-9
    ant_hill_node = ant_hill['ah_number']+11
    block_node = None

    if(ant_hill['service_1']):
        for node in block_color_dict:
            if(block_color_dict[node]==ant_hill['service_1']):
                block_node = node
                node = None
                move_to_node(block_node)
                talk_to_arduino("P")
                move_to_node(ant_hill_node)
                talk_to_arduino("T180")
                talk_to_arduino("O-20")
                talk_to_arduino("L")
                talk_to_arduino("O8")
                talk_to_arduino("P")
                break

    if(ant_hill['service_2']):
        for node in block_color_dict:
            if(block_color_dict[node]==ant_hill['service_2']):
                block_node = node
                node = None
                move_to_node(block_node)
                talk_to_arduino("P")
                move_to_node(ant_hill_node)
                talk_to_arduino("T180")
                talk_to_arduino("O-20")
                talk_to_arduino("R")
                talk_to_arduino("O8")
                talk_to_arduino("P")
                break

    if(ant_hill['trash']):
        move_to_node(ant_hill_node)
        trash_node = None
        if(ant_hill['service_1']):
            trash_node = service_2_node
        elif(ant_hill['service_2']):
            trash_node = service_1_node
        
        if(trash_node==service_1_node):
            talk_to_arduino("T180")
            talk_to_arduino("O-20")
            talk_to_arduino("L")
            talk_to_arduino("O8")
        elif(trash_node==service_2_node):
            talk_to_arduino("T180")
            talk_to_arduino("O-20")
            talk_to_arduino("L")
            talk_to_arduino("O8")
        else:
            talk_to_arduino("T180")
            talk_to_arduino("O-20")
            talk_to_arduino("L")
            talk_to_arduino("O8")
            camera.capture("Trash.jpg")
            rawCapture.truncate(0)
            result = detection.detect_color("Trash.jpg",45)
            if(result == False):
                talk_to_arduino("O-20")
                talk_to_arduino("R")
                talk_to_arduino("R")
                talk_to_arduino("O8")

        talk_to_arduino("P")
        move_to_node(2)
        if(first_trash_deposited == 0):
            turn_angle = 30
        else:
            turn_angle = -30
        turn(turn_angle)
        talk_to_arduino("P")
        turn(turn_angle)

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
    binary_string = bin(id)
    binary_string = '0'*(8-len(self.binary_string)) + self.binary_string #To add preceding zeros
    ant_hill['is_qah'] = int(binary_string[0],2)
    ant_hill['ah_number'] = int(self.binary_string[1,3],2)
    ant_hill['service_2'] = int(self.binary_string[3,5],2)
    ant_hill['service_1']  = int(self.binary_string[5,7],2)
    ant_hill['trash'] = int(self.binary_string[7])
    return ant_hill

def create_all_services():
    global ant_hill_list
    block_services = []
    trash_services = []
    final_services = []

    for ant_hill in ant_hill_list:
        ant_hill_node = ant_hill['ah_number']+11
        services = []
        if(ant_hill['service_1']):
            services.append((ant_hill_node,1,ant_hill['service_1']))
        if(ant_hill['service_2']):
            services.append((ant_hill_node,2,ant_hill['service_2']))
        if(ant_hill['trash']):
            services.append((ant_hill_node,3,None))

        if(ant_hill['is_qah']):
            final_services.extend(services)
        else:
            for service in services:
                if(service[1] == 3):
                    trash_services.append(service)
                else:
                    block_services.append(service)

    while(block_services and trash_services):
        if(not final_services or final_services[-1][1] == 3):
            service = block_services.pop()
            final_services.append(service)
        else:
            last_service = final_services[-1]
            flag = 1
            for service in trash_services:
                if(service[0] == last_service[0]):
                    trash_services.remove(service)
                    final_services.append(service)
                    flag = 0
            if(flag):
                present_node = final_services[-1][0]
                opposite_nodes_list = [[11,14],[12,13]]
                for nodes in opposite_nodes_list:
                    if(present_node in nodes):
                        opposite_node = sum(nodes) - present_node
                flag = 1
                for service in block_services:
                    if(service[0] == opposite_node):
                        flag = 0
                if(flag):
                    for service in trash_services:
                        if(service[0] == opposite_node):
                            trash_services.remove(service)
                            final_services.,append(service)

    final_services.extend(block_services)
    final_services.extend(trash_services)
    return final_services

def execute_service(service):
    if(service[1] == 3):
        move_to_node(service(0))
        

    else:
        #Supply block

def right_service():
    pass

def left_service():
    pass


'''
* Function Name: talk_to_arduino
* Input: action -> Message that has to be sent to arduino
* Output: 
* Logic: Sends the message to arduino and waits for a job done signal.
*
* Example Call: talk_to_arduino("M1")
'''
def talk_to_arduino(action):
    global serial_communication
    print("Talking to arduino:",action)
    serial_communication.write(action.encode())
    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline().decode().strip("\n").strip("\r")
            if response == "Job done":
                break
            else:
                print(response)

if __name__ == "__main__":
    time.sleep(2)
    run_bot()
