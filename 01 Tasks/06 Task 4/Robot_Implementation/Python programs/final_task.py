import serial 
import time

serial_communication = serial.Serial('/dev/ttyUSB0',9600)

def talk_to_arduino(action):
    global serial_communication

    serial_communication.write(action.encode())

    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline().decode().strip("\n").strip("\r")
            if response == "Job done":
                break

l = [
#    'D', 'D', 'I','M1','L','M1','M1','L','T45','D','L','D','T-45','D','T-45','M1','M1', #Block A
#    'M1','M1','R','T-45','D','R','D','T45','D','R','M1','M1','R',                       #Block B

#    'M1','T-45','D','R','T45','D','R','T45','D','R','T45','D','R',                     #Aruco
    
    #AH2
    'L','M1','L','M1','R','O8','P','O-10','R','M1','R','M1','R','M1','R','N','M1','T180','O-20','L','O8','P',
    'O-30','R','M1','L','M1','L','M1',
    'R','M1','M1','M1','L','O8','P','O-10','L','M1','M1','M1','L','M1','R','M1','R','N','M1','T180','O-20','R','O8','P',
    
    #AH0
    'O-30','L','M1','L','M1','L','M1',
    'R','M1','L','O8','P','O-10','L','M1','L','M1','L','M1','R','N','M1','T180','O-20','R','O8','P',

    #AH1
    'O-30','L','M1','L','M1','M1','L','N','M1','T180','O-20','R','O8','P','O-30','L','M1','R','M1','R','M1','M1','T-35','P'

    #AH3
    'T35','O-30','L','M1','M1'
    'R','M1','M1','L','O8','P','O-10','L','M1','M1','L','M1','L','M1','L','N','M1','T180','O-20','R','O8','P'
    'O-30','L','L','O8','P','O-30','R','M1','R','M1','L','M1','M1','T35','P'

    #END
    'T35','O-30','L','M1','M1','M1'
]

if __name__ == "__main__":
    try:
        for i in l:
            if(i[0] == 'D'):
                print(i[2:])
                time.sleep(1)
            else:
                print(i)
                talk_to_arduino(i)
    except KeyboardInterrupt:
        talk_to_arduino("X")
        print("Closing")