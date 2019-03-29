'''
Last edited by Karthik K Bhat
Last edit time: 18 Feb 2019
'''

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

red_led_pin = 15
green_led_pin = 19
blue_led_pin = 21

GPIO.setup(red_led_pin,  GPIO.OUT)
GPIO.setup(green_led_pin, GPIO.OUT)
GPIO.setup(blue_led_pin,  GPIO.OUT)

red_led = GPIO.PWM(red_led_pin, 50)
green_led = GPIO.PWM(green_led_pin, 50)
blue_led = GPIO.PWM(blue_led_pin, 50)

red_led.start(100)
green_led.start(100)
blue_led.start(100)

def turn_on_led(led_color):
    global red_led, green_led, blue_led
    if led_color == 1:
        red_led.ChangeDutyCycle(0)
        green_led.ChangeDutyCycle(100)
        blue_led.ChangeDutyCycle(100)

    elif led_color == 2:
        red_led.ChangeDutyCycle(100)
        green_led.ChangeDutyCycle(0)
        blue_led.ChangeDutyCycle(100)

    elif led_color == 3:
        red_led.ChangeDutyCycle(100)
        green_led.ChangeDutyCycle(100)
        blue_led.ChangeDutyCycle(0)

    elif led_color == 4:
        green_led.ChangeDutyCycle(0)
        red_led.ChangeDutyCycle(40)
        blue_led.ChangeDutyCycle(100)

    time.sleep(1)


def turn_off_led():
    red_led.ChangeDutyCycle(100)
    green_led.ChangeDutyCycle(100)
    blue_led.ChangeDutyCycle(100)

def end_led():
    red_led.stop()
    blue_led.stop()
    green_led.stop()

if __name__ == "__main__":

    time.sleep(1)
    for i in range(1,5):
        turn_off_led()
        time.sleep(1)
        print(i)
        turn_on_led(i)
    end_led()
    GPIO.cleanup()

