import serial
import detection
from ant_hill import ah
import time
#from picamera import PiCamera 
#from picamera.array import PiRGBArray

#Globals

NORTH = 0
NORTH_EAST = 0.5
EAST = 1
SOUTH_EAST = 1.5
SOUTH = 2
SOUTH_WEST = 2.5
WEST = 3
NORTH_WEST = 3.5

position = None
direction = None

serial_communication = serial.Serial('/dev/ttyUSB0',9600)
bot_position = -1
bot_direction = NORTH

'''
res = (608, 368)    # resolution for the frame

camera = PiCamera()      # To initialize the PiCamera
camera.resolution = res  # set the resolution of the camera
camera.rotation = 180    # to rotate the frames by 180 degrees
camera.framerate = 16    # Set the frame rate
rawCapture = PiRGBArray(camera, size=res)
'''

arena_map = {
    -16: SOUTH,-15: WEST,-14: EAST,-13: WEST,-12: EAST,-11: WEST,-10: EAST,-9: WEST,-8: EAST,-7: NORTH,-6: NORTH,-5: NORTH,-4: NORTH,-3: NORTH,-2: NORTH,-1: NORTH,
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
        13: [{-16,-15,-14,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,14},{-13},set(),{-12}],
        14: [{-16,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13},{-15},set(),{-14}],
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

ah_list = []
block_list = []
distance_to_sim = 1 #Enter the hardcoded distance

def run_bot():

    #get_block_colour()
    
    get_sims()
    move_to_node(5)
    talk_to_arduino("P") #Pick Block
    
    '''
    for ah in ah_list:
        if(is_qah(ah)):
            service(ah)
            ah_list.remove(ah)
            break

    for ah in ah_list:
        service(ah)
    '''

def get_block_colour():
    move_to_node(4)
    for _ in range(3):
        turn(-45)
        block_list.append(detect_colour())
    turn(-45)
    move_to_node(7)
    for _ in range(3):
        turn(45)
        block_list.append(detect_colour())
    turn(45)
    move_to_node(0)

def get_sims():
    global distance_to_sim

    move_to_node(1)
    for i in range(2):
        move(2*i,distance_to_sim)
        turn(-90)
        #camera.capture("picture"+str(i*2)+".jpg")
        #rawCapture.truncate(0)
        #id = detection.detect_sim_id("./picture"+str(i*2)+".jpg")
        #print(id)
        turn(180)
        #camera.capture("picture"+str(i*2+1)+".jpg")
        #rawCapture.truncate(0)
        #id = detection.detect_sim_id("./picture"+str(i*2+1)+".jpg")
        #print(id)
        turn(90)
        move((2*i+2)%4,distance_to_sim)

def move(direction, distance = 0):

    global bot_direction,bot_position

    turn_angle = min(abs(direction - bot_direction),abs(direction-bot_direction+4))*90
    sign = -1 if bot_direction+2<direction else 1
    turn(turn_angle*sign)
    
    position = immediate_node[bot_position][direction]
    print("Moving to node",position)
    talk_to_arduino("M",str(distance))

def turn(angle):
    global bot_direction

    bot_direction = (bot_direction + angle/90)%4
    print("Turning",angle,"degrees")
    print("Now facing",bot_direction)
    #encoded_angle = ((angle+180)*8)//360
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

def detect_colour():
    pass

def is_qah(ah):
    pass

def service(ah):
    pass

def get_sim_id():
    return 0

def talk_to_arduino(action, value=None):
    global serial_communication

    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline()
        if response == "1":
            break
        time.sleep(1)
    
    serial_communication.write(action.encode())
    
    if(value is not None):
        serial_communication.write(value.encode())

if __name__ == "__main__":
    run_bot()