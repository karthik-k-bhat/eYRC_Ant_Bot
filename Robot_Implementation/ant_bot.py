from ant_hill import ah

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class ab:

    def __init__(self):
        self.position = -1
        self.direction = UP
        self.map = {
            -16: DOWN,
            -15: LEFT,
            -14: RIGHT,
            -13: LEFT,
            -12: RIGHT,
            -11: LEFT,
            -10: RIGHT,
             -9: LEFT,
             -8: RIGHT,
             -7: UP,
             -6: UP,
             -5: UP,
             -4: UP,
             -3: UP,
             -2: UP,
             -1: UP,
              0: [{-16,-15,-14,-13,-12,-11,-10,-9,-8,1,2,9,10,11,12,13,14},{-7,-6,-5,6,7,8},{-1},{-4,-3,-2,3,4,5}],
              1: [{-16,2},{-13,-12,-11,-10,12,13},{-7,-6,-5,-4,-3,-2,-1,0,3,4,5,6,7,8},{-15,-14,-9,-8,9,11,14}],
              2: [{-16},{},{-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,3,4,5,6,7,8,9,10,11,12,13,14},{}],
              3: [{},{-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-1,0,1,2,6,7,8,9,10,11,12,13,14},{-2},{-4,-3,4,5}],
              4: [{},{},{},{}],
              5: [{},{},{},{}],
              6: [{},{},{},{}],
              7: [{},{},{},{}],
              8: [{},{},{},{}],
              9: [{},{},{},{}],
             10: [{},{},{},{}],
             11: [{},{},{},{}],
             12: [{},{},{},{}],
             13: [{},{},{},{}],
             14: [{},{},{},{}],
        }

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
        for i in range(4):
            id = self.get_sim_id()
            self.ah_list.append(ah(id))
            self.turn(90)
        self.turn(45)

    def move(self, direction):
        pass
    
    def turn(self,angle):
        pass

    def move_to_node(self,node_number):
        pass

    def get_block_colour(self):
        pass

    def is_qah(self,ah):
        pass

    def service(self,ah):
        pass

    def get_sim_id(self):
        pass
    

if __name__ == "__main__":
    bot = ab()
    bot.run()