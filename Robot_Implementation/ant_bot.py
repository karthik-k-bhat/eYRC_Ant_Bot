from ant_hill import ah

class ab:

    def __init__(self):
        self.position = -1
        self.direction = 0
        ah0 = ah()
        ah1 = ah()
        ah2 = ah()
        ah3 = ah()
        self.ah = [ah0,ah1,ah2,ah3]

    def run(self):
        self.get_blocks()
        self.get_sims()
        

    def get_blocks(self):
        pass

    def get_sims(self):
    	pass

    def move(self, direction):
        pass
    
    def turn(self,angle):
        pass

    def move_to_node(self,node_number):
        pass

if __name__ == "__main__":
    bot = ab()
    bot.run()
