import serial
import time

serial_communication = serial.Serial('/dev/ttyUSB0',9600)

def talk_to_arduino(action):
    global serial_communication

    message = action.encode()
    serial_communication.write(message)

#Wait for pi to initialize
time.sleep(5)

try:
    while(1):
        s = input().split()
        talk_to_arduino(*s)
        while(1):
            if(serial_communication.in_waiting):
                response = serial_communication.readline()
                response = response.decode().strip('\n').strip('\r')
                if(response == "1"):
                    print('Job done.')
                    break
                else:
                    print(response)

except KeyboardInterrupt:
    print("Closing")