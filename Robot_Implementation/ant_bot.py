import serial
from ant_hill import ah

NORTH = 0
NORTH_EAST = 0.5
EAST = 1
SOUTH_EAST = 1.5
SOUTH = 2
SOUTH_WEST = 2.5
WEST = 3
NORTH_WEST = 3.5

class ab:

    def __init__(self):
        self.position = -1
        self.direction = NORTH
        
        self.arena_map = {
            -16: SOUTH,-15: WEST,-14: EAST,-13: WEST,-12: EAST,-11: WEST,-10: EAST,-9: WEST,-8: EAST,-7: NORTH,-6: NORTH,-5: NORTH,-4: NORTH,-3: NORTH,-2: NORTH,-1: NORTH,
              0: [{-16,-15,-14,-13,-12,-11,-10,-9,-8,1,2,9,10,11,12,13,14},{-7,-6,-5,6,7,8},{-1},{-4,-3,-2,3,4,5}],
              1: [{-16,2},{-13,-12,-11,-10,12,13},{-7,-6,-5,-4,-3,-2,-1,0,3,4,5,6,7,8},{-15,-14,-9,-8,9,11,14}],
              2: [{-16},{},{-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,3,4,5,6,7,8,9,10,11,12,13,14},{}],
              3: [{},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-1,0,1,2,6,7,8,9,10,11,12,13,14},{-2},{-4,-3,4,5}],
              4: [{},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-2,-1,0,1,2,3,6,7,8,9,10,11,12,13,14},{-3},{-4,5}],
              5: [{},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-3,-2,-1,0,1,2,3,4,6,7,8,9,10,11,12,13,14},{-4},{}],
              6: [{},{-7,-6,7,8},{-5},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-4,-3,-2,-1,0,1,2,3,4,5,9,10,11,12,13,14}],
              7: [{},{-7,8},{-6},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,9,10,11,12,13,14}],
              8: [{},{},{-7},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,9,10,11,12,13,14}],
              9: [{-9,-8,11},{-16,-13,-12,-11,-10,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,10,12,13},{-15,-14,14},{}],
             10: [{-11,-10,12},{},{-13,-12,13},{-16,-15,-14,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,11,14}],
             11: [{},{-9},{-16,-15,-14,-13,-12,-11,-10,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,12,13,14},{-8}],
             12: [{},{-11},{-16,-15,-14,-13,-12,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,13,14},{-10}],
             13: [{-16,-15,-14,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,14},{-13},{},{-12}],
             14: [{-16,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13},{-15},{},{-14}],
        }

        self.immediate_node = [
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

        self.ah_list = []
        self.block_list = []

    def run(self):

        self.get_blocks()
        self.get_sims()
        
        for ah in self.ah_list:
            if(self.is_qah(ah)):
                self.service(ah)
                self.ah_list.remove(ah)
                break

        for ah in self.ah_list:
            self.service(ah)

    def get_blocks(self):
        self.move_to_node(4)
        for _ in range(3):
            self.turn(-45)
            self.block_list.append(self.get_block_colour())
        self.turn(-45)
        self.move_to_node(7)
        for _ in range(3):
            self.turn(45)
            self.block_list.append(self.get_block_colour())
        self.turn(45)
        self.move_to_node(0)

    def get_sims(self):
        self.move_to_node(1)
        self.turn(-45)
        for _ in range(4):
            id = self.get_sim_id()
            self.ah_list.append(ah(id))
            self.turn(90)
        self.turn(45)

    def move(self, direction, distance = 0):
        pass
    
    def turn(self, direction):
        pass

    def move_to_node(self,node_number):
        while self.position != node_number:
            for i in range(4):
                if node_number in self.arena_map[self.position][i]:
                    self.move(i)
                    self.position = self.immediate_node[self.position][i]
                    break

    def get_block_colour(self):
        pass

    def is_qah(self,ah):
        pass

    def service(self,ah):
        pass

    def get_sim_id(self):
        return 0
    

if __name__ == "__main__":
    bot = ab()
    bot.run()