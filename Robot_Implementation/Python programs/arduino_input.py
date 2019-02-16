import serial
import time

serial_communication = serial.Serial('/dev/ttyUSB0',9600)

def talk_to_arduino(action, value=None):
    global serial_communication

    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline().decode().strip("\n").strip("\r")
        if response == "1":
            print("Job Done")
            break
        else:
            print(response)
        time.sleep(1)

    serial_communication.write(action.encode())
    
    if(value is not None):
        serial_communication.write(value.encode())

#Wait for pi to initialize
time.sleep(5)

try:
    while(1):
        s = input().split()
        talk_to_arduino(*s)

except KeyboardInterrupt:
    print("Closing")