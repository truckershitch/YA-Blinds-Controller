"""MQTT Handler for Playroom Blinds Controller"""
from mqtt_handler_master import MQTTHandler
from config_esp8266 import debug_print

class BlindsMQTTHandler(MQTTHandler):
    """MQTTHandler subclass for blinds"""

    def __init__(self):
        super().__init__(self.sub_cb)
        # super().connect_and_subscribe(PumpMQTTHandler.sub_cb)

    def sub_cb(self, topic, msg):
        """Callback for MQTT subscribe"""
        import ujson

        debug_print('Received msg: %s topic: %s' % (msg, topic))
        try:
            self._message = ujson.loads(msg.decode())
        except ValueError as e:
            print('Error decoding JSON string %s\n%s' % (msg, e))
