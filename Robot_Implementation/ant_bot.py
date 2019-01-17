from ant_hill import ah

Up = 0
Right = 1
Down = 2
Left = 3

class ab:

    def __init__(self):
        self.position = -1
        self.direction = Up
        self.map = {
            -16: Down,
            -15: Left,
            -14: Right,
            -13: Left,
            -12: Right,
            -11: Left,
            -10: Right,
             -9: Left,
             -8: Right,
             -7: Up,
             -6: Up,
             -5: Up,
             -4: Up,
             -3: Up,
             -2: Up,
             -1: Up,
              0: [{-16,-15,-14,-13,-12,-11,-10,-9,-8,1,2,9,10,11,12,13,14},{-7,-6,-5,6,7,8},{-1},{-4,-3,-2,3,4,5}],
              1: [{},{},{},{}],
              2: [{},{},{},{}],
              3: [{},{},{},{}],
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
        self.move_to_node(1)

    def get_sims(self):
    	pass

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

    

if __name__ == "__main__":
    bot = ab()
    bot.run()
