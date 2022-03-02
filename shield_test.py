# test cnc shield motor x

from machine import Pin
from utime import sleep_us

en_pin = Pin(12, Pin.OUT)

REVS = 2

# # Pins for CNC Shield for Wemos D1 R32
# # Motor X, Y, Z
# steps = [26, 25, 17]
# dirs = [16, 27, 14]
# labels = ['X', 'Y', 'Z']

# Pins for CNC Shield for Wemos D1 R1
# Motor X, Y, Z
steps = [16, 5, 4]
dirs = [14, 12, 13]
labels = ['X', 'Y', 'Z']


step_pin = []
for pin in steps:
    step_pin.append(Pin(pin, Pin.OUT))

dir_pin = []
for pin in dirs:
    dir_pin.append(Pin(pin, Pin.OUT))

en_pin.value(0) # enabled LOW

# for motor in range(3):
for motor in [1]:

    for dir_flag in range(2):
        dir_flag = (dir_flag + 1) % 2
        dir_pin[motor].value(dir_flag)

        print('Motor %s Direction %d' % (labels[motor], dir_flag))

        for _rev in range(REVS):

            for _i in range(2048):
                step_pin[motor].value(1)
                sleep_us(500)
                step_pin[motor].value(0)
                sleep_us(500)
                print('Motor %s Direction %d Step %d' %
                    (labels[motor], dir_flag, _i))

            sleep_us(1000 * 1000)

    sleep_us(1000 * 1000)

en_pin.value(1) # disabled HIGH
