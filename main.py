"""
main.py for Blinds Controller
"""

from blind_controller import BlindController
from errorwrapper import ErrorWrapper
from config_esp8266 import ERROR_FILE

wrapper = ErrorWrapper(ERROR_FILE)
blind_controller = BlindController()
wrapper.wrap(blind_controller, 'loop')
