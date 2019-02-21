'''
Last edited by Karthik K Bhat
Last edit time: 18 Feb 2019
'''

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

red_led_pin = 18
green_led_pin = 19
blue_led_pin = 20

GPIO.setup(red_led_pin,  GPIO.OUT)
GPIO.setup(green_led_pin, GPIO.OUT)
GPIO.setup(blue_led_pin,  GPIO.OUT)

red_led = GPIO.PWM(red_led, 50)
green_led = GPIO.PWM(green_led, 50)
blue_led = GPIO.PWM(blue_led, 50)

red_led.start(100)
green_led.start(100)
blue_led.start(100)

def turn_on_led(led_color):
    global red_led, green_led, blue_led
    global led_on_time
    if led_color = 'R':
        red_led.ChangeDutyCycle(0)
        green_led.ChangeDutyCycle(100)
        blue_led.ChangeDutyCycle(100)
        led_on_time = time.time()
        
    elif led_color = 'G':
        red_led.ChangeDutyCycle(100)
        green_led.ChangeDutyCycle(0)
        blue_led.ChangeDutyCycle(100)
        led_on_time = time.time()

    elif led_color = 'B':
        red_led.ChangeDutyCycle(100)
        green_led.ChangeDutyCycle(100)
        blue_led.ChangeDutyCycle(0)
        led_on_time = time.time()

    elif led_color = 'Y':
        red_led.ChangeDutyCycle(70)
        green_led.ChangeDutyCycle(70)
        blue_led.ChangeDutyCycle(100)
        led_on_time = time.time()


def turn_off_led():
    red_led.ChangeDutyCycle(100)
    green_led.ChangeDutyCycle(100)
    blue_led.ChangeDutyCycle(100)
        
    

if __name__ == __main__:
    for i in ['R','G','B','Y']:
        turn_on_led(i)
        while (led_on_time - time.time()) <= 1 :
            pass
        turn_off_led()


