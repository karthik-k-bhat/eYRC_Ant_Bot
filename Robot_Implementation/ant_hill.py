class ah:
    def __init__(self,id):
        self.binary_string = bin(id)
        self.binary_string = '0'*(8-len(self.binary_string)) + self.binary_string
        self.is_qah = self.binary_string[0]
        self.ah_number = int(self.binary_string[],2)
        