
import serial
import time
from picamera import PiCamera
from picamera.array import PiRGBArray

# Camera
resolution = (640, 480)                   # resolution for the frame
camera = PiCamera()                       # To initialize the PiCamera
camera.resolution = resolution            # set the resolution of the camera
camera.framerate = 16                     # Set the frame rate
rawCapture = PiRGBArray(camera, size=resolution)
camera.rotation = 90

serial_communication = serial.Serial('/dev/ttyUSB0',9600)

def talk_to_arduino(action):
    global serial_communication

    serial_communication.write(action.encode())

    while(1):
        if(serial_communication.in_waiting>0):
            response = serial_communication.readline().decode().strip("\n").strip("\r")
            print(response)
            if response == "Job done":
                break


if __name__ == "__main__":
    #Wait for pi to initialize
    time.sleep(2)
    print("Start")
    try:
        while(1):
            s = input().split()[0]
            if(s == "ph"):
                name = input("Enter photo name: ")
                camera.start_preview()
                time.sleep(1)
                camera.capture(name+".jpg")
                rawCapture.truncate(0)
                camera.stop_preview()
                print("Done")
                continue
            talk_to_arduino(s)

    except KeyboardInterrupt:
        talk_to_arduino("X")
        print("Closing")
