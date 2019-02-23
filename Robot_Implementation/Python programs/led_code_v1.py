import wiringpi as wp
import time

wp.wiringPiSetupGpio()

red_led = xx
green_led = xx
blue_led = xx

wp.pinMode(red_led, 1)
wp.pinMode(green_led, 1)
wp.pinMode(blue_led, 1)

wp.softPwmCreate(red_led, 0, 255)
wp.softPwmCreate(green_led, 0, 255)
wp.softPwmCreate(blue_led, 0, 255)

def turn_on_led(led_color):
    global red_led, green_led, blue_led
    global led_on_time
    if led_color = 'R':
        wp.softPwmWrite(red_led, 0)
        wp.softPwmWrite(green_led, 255)
        wp.softPwmWrite(blue_led, 255)
        led_on_time = time.time()
        
    elif led_color = 'G':
        wp.softPwmWrite(red_led, 255)
        wp.softPwmWrite(green_led, 0)
        wp.softPwmWrite(blue_led, 255)
        led_on_time = time.time()

    elif led_color = 'B':
        wp.softPwmWrite(red_led, 255)
        wp.softPwmWrite(green_led, 255)
        wp.softPwmWrite(blue_led, 0)
        led_on_time = time.time()

    elif led_color = 'Y':
        wp.softPwmWrite(red_led, 200)
        wp.softPwmWrite(green_led, 200)
        wp.softPwmWrite(blue_led, 255)
        led_on_time = time.time()


def turn_off_led():
    wp.softPwmCreate(red_led, 255)
    wp.softPwmWrite(green_led, 255)
    wp.softPwmWrite(blue_led, 255)
    

if __name__ == __main__:
		turn_off_led()
    for i in ['R','G','B','Y']:
        turn_on_led(i)
        while (led_on_time - time.time()) <= 1 :
            pass
        turn_off_led()
