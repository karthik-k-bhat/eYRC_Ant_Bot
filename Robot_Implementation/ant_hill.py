class ah:
    def __init__(self,id):
        self.binary_string = bin(id)
        self.binary_string = '0'*(8-len(self.binary_string)) + self.binary_string
        self.is_qah = self.binary_string[0]
        self.ah_number = int(self.binary_string[1,3],2)
        self.service_2 = int(self.binary_string[3,5],2)
        self.service_1 = int(self.binary_string[5,7],2)
        self.thrash = int(int(self.binary_string[7]))