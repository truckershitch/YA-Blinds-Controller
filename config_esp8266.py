"""
config.py
Parameter file for Playroom Blinds
Used by:
- blind_controller.py
- set_rtc.py
- mqtt_handler_blinds.py
- rtcmem_handler_blinds.py
"""

from machine import Pin

# Print debugging messages
#
DEBUG = True
#
# sock_xfer_client/server settings
#
ESP_IP = '192.168.1.125'
XFER_PORT = 4455
BLOCK_SIZE = 128
#
BOOT_CHOICES = { # written to RTC memory
    'blinds': 'B',
    'transfer': 'T'
}
BOOT_CHOICE_FILE = 'next_boot.txt' # will blinds or uftpd server run on next boot?
ERROR_FILE = 'error.log'
POS_FILE = 'cur_pos.txt'
#
# NTP Settings
#
NTP_SERVERS = ['192.168.1.1']
TZ = -5
DST = True
COUNTRY = 'US'

STEPS_PER_REV = 2048 # Steps for one revolution of 28BYJ-48 Motor
MICROSEC_DELAY = 500 # Delay in microseconds between steps

# Pin to enable all motors on CNC Shield
EN_PIN = Pin(0, Pin.OUT)

# Motor and Pin data for CNC Shield
# for Wemos D1 R1 ESP8266
#
# Convert 28BYJ-48 motors to bipolar
# Cut the red motor wire
# WIRE ORDER: Blue Yellow Pink Orange
# Dupont plug orientation doesn't matter
# Cat5 ethernet cable for cable run
# One pair eth. wires to each motor lead
# Blues to Blue, Browns to Yellow,
# Greens to Pink, Oranges to Orange

MOTOR_CLOSE_DIR_VAL = 0 # (0 or 1) Value that sets motor to 'close blind' direction
MOTOR_DIR_POLARITY = MOTOR_CLOSE_DIR_VAL # (Same as close blind direction value)
MOTOR_DATA = {
    'left': {
        'cnc_label': 'X',
        'step': Pin(16, Pin.OUT),
        'dir': Pin(14, Pin.OUT),
        'revs': 2.05 # adjust for your setup
    },
    'middle': {
        'cnc_label': 'Y',
        'step': Pin(5, Pin.OUT),
        'dir': Pin(12, Pin.OUT),
        'revs': 2 # adjust for your setup
    },
    'right': {
        'cnc_label': 'Z',
        'step': Pin(4, Pin.OUT),
        'dir': Pin(13, Pin.OUT),
        'revs': 1.9 # adjust for your setup
    }
}

# helper functions

def debug_print(*args, **kw_args):
    """Print debuggins messages"""
    if DEBUG:
        print(*args, **kw_args)
        