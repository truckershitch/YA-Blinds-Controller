"""
MQTT Client Handler

Created March 2021
Modified May 22, 2021
"""

from umqtt.simple import MQTTClient
from config_esp8266 import debug_print
import mqtt_cred

class MQTTHandler():
    """MQTT Client Class"""

    def __init__(self, sub_cb, dev_name=mqtt_cred.DEVICE_NAME, client_name=mqtt_cred.CLIENT_NAME, clean_session=True):
        self._sub_cb = sub_cb # callback for received messages
        self._device_name = dev_name
        self._client_name = client_name
        self._is_clean_session = clean_session
        self._message = None
        self._paused = 'off'
        self._err_prefix = '*** MQTT Handler OSError ***'
        self._mqtt_reconnect_msg = 'Reconnecting to MQTT Broker'
        self._client = None
        self.sub_topic = None

    def init_client(self, topic):
        """Initialize MQTT Client"""
        client = MQTTClient(
            self._client_name,
            mqtt_cred.BROKER,
            mqtt_cred.PORT,
            mqtt_cred.USER,
            mqtt_cred.PASS,
            keepalive=60
        )
        self._client = client
        self.sub_topic = topic
        try:
            return self.connect_and_subscribe()
        except OSError:
            return self.reconnect()

    def connect_and_subscribe(self):
        """Connect MQTT client and subscribe to topic"""
        self._client.set_callback(self._sub_cb)
        self._client.connect(self._is_clean_session)
        self._client.subscribe(self.sub_topic.encode())

        debug_print('Connected to %s, subscribed to %s topic.' %
            (mqtt_cred.BROKER, self.sub_topic))

        self._paused = 'off'

    def reconnect(self, count=1):
        max_count = 15
        intvl = 60 # 1 minute

        if count > max_count:
            raise RuntimeError('MQTT Reconnection failed')

        try:
            from utime import sleep
            secs = intvl
            print('MQTT Broker Reconnection Attempt %d of %d'
                % (count, max_count))
            print('Sleeping %d seconds before reconnecting' % secs)
            sleep(secs)
            return self.connect_and_subscribe()
        except OSError as e:
            print('Exception reconnecting to MQTT Broker: %s' % e)
            print('Calling reconnect() again')
            return self.reconnect(count=(count + 1))

    def send_mqtt_message(self, topic, msg, retain=False):
        """Publish message to MQTT Broker"""
        def publish():
            """Call MQTT publish()"""
            try:
                self._client.publish(topic, msg.encode(), retain=retain)
                return True
            except OSError as e:
                err_msg = ('%sFailed to send %s: %s' %
                    (self._err_prefix, msg_tail, e))
                print('\n%s\n%s' %
                    (err_msg, self._mqtt_reconnect_msg))
                self.reconnect()
                return False

        retain_tail = ''
        if retain:
            retain_tail = ' <retained>'

        msg_tail = ('payload "%s" to MQTT Broker %s topic %s%s.\n'
            % (msg, mqtt_cred.BROKER, topic, retain_tail))

        if publish():
            print('Sent %s' % msg_tail)
        # else:
        #     print('Attempting to rebpublish payload.')
        #     print('Calling connect_wifi.reconnect()')
        #     from connect_wifi import reconnect
        #     reconnect()
        #     print('Attempting to connect to MQTT Broker')
        #     self.connect_and_subscribe()
        #     if not publish():
        #         secs = 3
        #         from machine import reset
        #         print('Sleeping %d seconds then calling machine.reset()' % secs)
        #         reset()

    def clear_read_message(self):
        """Clear message after it has been received"""
        self._message = None

    def print_paused_status(self):
        """Set paused status"""
        print('%s Paused Status: %s.\n' % (self._device_name, self._paused))

    def msg_received_blocking(self):
        """Blocking call for initial status"""
        self._client.wait_msg()

    def fetch_message(self):
        """Return None if no message has been received"""
        try:
            self._client.check_msg()
            msg = self._message

            return msg
        except OSError as e:
            err_msg = ('%sFailed to check MQTT messages: %s' %
                (self._err_prefix, e))
            print('\n%s\n' % err_msg)
            print('\n%s\n%s' %
                (err_msg, self._mqtt_reconnect_msg))
            self.reconnect()
            