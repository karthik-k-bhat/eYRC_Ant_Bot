import serial
import time

serial_communication = serial.Serial('/dev/ttyUSB0',9600)

def talk_to_arduino(action, value=None):
    global serial_communication

    serial_communication.write(action.encode())

    if(value is not None):
        serial_communication.write(value.encode())

    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline().decode().strip("\n").strip("\r")
            print(response)
            if response == "Job done":
                break


if __name__ == "__main__":
    #Wait for nano to initialize
    time.sleep(2)
    try:
        print("1. T45 Check.")
        print("2. Ant-Hill Service check.")
        print("3. ")
        choice = int(input())


    except KeyboardInterrupt:
        talk_to_arduino("X")
        print("Closing")
