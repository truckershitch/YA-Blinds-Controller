"""
Playroom Blinds Tilt (open/close) Automation
blind_controller.py

Created April 22, 2021
Last Modified June 8, 2021

BlindController._pos: percent open (int)
0 = closed, 100 = open
"""

from utime import ticks_ms, ticks_diff, time, sleep, sleep_us
import config_esp8266 as config
import mqtt_cred
import mqtt_handler_blinds
from set_rtc import configure_time

class BlindController:
    """Class to control blinds"""

    def __init__(self):
        config.EN_PIN.value(1) # turn off enable pin
        self.mqtt_handler = mqtt_handler_blinds.BlindsMQTTHandler()
        self._pos = 0

        self.get_initial_status()

    def _set_pos(self, pos):
        """Save overall blinds position"""
        self._pos = pos

    def _get_pos(self):
        """Return overall blinds position"""
        return self._pos

    def publish(self, topic, msg, retain=False):
        """Publish a MQTT message"""
        self.mqtt_handler.send_mqtt_message(topic, msg, retain=retain)

    def _send_heartbeat(self):
        """Publish heartbeat (timestamp) to MQTT broker"""
        self.publish(mqtt_cred.TOPIC_HB, '{"type": "hb", "ts": %d, "pos": %d}' %
            (time(), self._pos))

    def get_initial_status(self):
        """Read initial blinds position from MQTT Broker"""
        self.mqtt_handler.init_client(mqtt_cred.TOPIC_STAT)

        dbg_msg = 'Blinds Position '
        found = False
        pos = 100
        for i in range(5):
            sleep(1)
            new_msg = self.mqtt_handler.fetch_message()
            if new_msg is None:
                config.debug_print('No message found in pass %d' % (i + 1))
            else:
                self.mqtt_handler.clear_read_message()
                pos = new_msg['pos']
                found = True
                break

        self._set_pos(pos)

        if found:
            dbg_msg += 'found!'
        else:
            dbg_msg += 'not found!'
            self.send_status()

        config.debug_print(dbg_msg + '  Setting to %d%%' % pos)
        self.mqtt_handler.init_client(mqtt_cred.TOPIC_SUB)

    def send_status(self):
        status_msg = '{"type": "stat", "pos": %d}' % self._get_pos()
        self.publish(mqtt_cred.TOPIC_STAT, status_msg, retain=True)

    def move_single_blind(self, window, direction, pct=10):
        """Move individual blind"""
        dir_tbl = {
            'open': {
                'pin_val': (config.MOTOR_DIR_POLARITY + 1) % 2,
                'gerund': 'Opening'
            },
            'close': {
                'pin_val': config.MOTOR_DIR_POLARITY,
                'gerund': 'Closing'
            }
        }
        steps_to_take = int(config.MOTOR_DATA[window]['revs'] * config.STEPS_PER_REV * pct / 100)

        try:
            dir_flag = dir_tbl[direction]['pin_val']
            dir_ger = dir_tbl[direction]['gerund']
        except KeyError:
            print('Invalid direction! %s' % direction)
            return

        print('%s %s blind %d%%\n' % (dir_ger, window, pct))

        config.MOTOR_DATA[window]['dir'].value(dir_flag)
        config.EN_PIN.value(0) # start the grill!

        for _ in range(steps_to_take):
            config.MOTOR_DATA[window]['step'].value(1)
            sleep_us(config.MICROSEC_DELAY)
            config.MOTOR_DATA[window]['step'].value(0)
            sleep_us(config.MICROSEC_DELAY)

        config.EN_PIN.value(1) # take a nap

    def set_blinds_position(self, new_pos):
        """Set position of blinds as percent open"""
        cur_pos = self._get_pos()
        pct_diff = new_pos - cur_pos

        if pct_diff == 0:
            print('new_pos == cur_pos -- not moving blinds!')
            return

        dir_flag = 'open' if pct_diff > 0 else 'close'

        # Move blinds - Sort by cnc_label attribute
        for b in sorted(config.MOTOR_DATA.items(),
          key=lambda k_v: k_v[1]['cnc_label']):
            self.move_single_blind(b[0], dir_flag, abs(pct_diff))
            sleep_us(1 * 1000 * 1000) # 1 second between blinds

        self._set_pos(new_pos)
        self.send_status()

    def handle_msg(self, msg):
        """Handle MQTT message"""
        msg_type = msg['type']

        def force_range(val, range_min=0, range_max=100):
            """Hack to put value in range"""
            int_val = 0

            try:
                int_val = int(val)
            except ValueError:
                print_error('Not an integer value: %s' % val)
                return None

            new_val = max(min(int_val, range_max), range_min)
            if int_val < range_min or int_val > range_max:
                print_error('New postion %d out of range: Set to %d' %
                    (int_val, new_val))

            return new_val

        def print_error(extra_msg=None):
            err_msg = 'Error with MQTT message: %s' % msg
            if extra_msg is not None:
                err_msg += '\n%s' % extra_msg
            print(err_msg)

        def check_val(val_type):
            if val_type not in ['pos', 'pct']:
                return (None, 'Invalid data type! Must be "pos" or "pct"')
            try:
                msg_val = msg[val_type]
            except KeyError:
                if val_type == 'pos':
                    return (None, 'No position specified!')
                return (None, 'No percentage specified!')

            # val_range_chk = None
            # if val_type == 'pct':
            #     val_range_chk = force_range(self._get_pos() + msg_val)
            # else:
            #     val_range_chk = force_range(msg_val)

            sign = 1 if msg_val >= 0 else -1
            val_range_chk = force_range(abs(msg_val))

            if val_range_chk is not None:
                return (val_range_chk * sign, None)

            return (None, 'Invalid %s! %s' % (val_type, msg_val))

        # def check_dir():
        #     try:
        #         dir_chk = msg['dir'].lower()
        #     except KeyError:
        #         return (None, 'No direction specified!')
        #     if dir_chk in ['open', 'close']:
        #         return (dir_chk, None)

        #     return (None, 'Invalid direction! %s' % dir_chk)

        # def check_pct_and_dir():
        #     pct_chk = check_val('pct')
        #     if pct_chk[0] is not None:
        #         dir_chk = check_dir()
        #         if dir_chk[0] is not None:
        #             return (pct_chk[0], dir_chk[0])
        #         return (None, dir_chk[1])
        #     return (None, pct_chk[1])

        def check_win():
            try:
                win_chk = msg['window'].lower()
            except KeyError:
                return (None, 'No window specified!')
            if win_chk in config.MOTOR_DATA.keys():
                return (win_chk, None)

            return (None, 'Invalid window! %s' % win_chk)

        if msg_type == 'open':
            return self.set_blinds_position(100)

        if msg_type == 'close':
            return self.set_blinds_position(0)

        if msg_type == 'rot':
            # partially rotate blinds by percentage

            # pct_dir_tuple = check_pct_and_dir()
            # if pct_dir_tuple[0] is None:
            #     return print_error(pct_dir_tuple[1])

            # # get the job done
            # sign = 1 if pct_dir_tuple[1] == 'open' else -1
            # return self.set_blinds_position(
            #   force_range(self._get_pos() + sign * pct_dir_tuple[0])
            # )

            chk_pct = check_val('pct')
            if chk_pct[0] is None:
                return print_error(chk_pct[1])

            return self.set_blinds_position(
                force_range(self._get_pos() + chk_pct)
            )

        if msg_type == 'pos':
            # set blind open percentage
            pos_check = check_val('pos')
            if pos_check[0] is not None:
                return self.set_blinds_position(pos_check[0])

            return print_error(pos_check[1])

        if msg_type == 'set':
            # set position
            pos_check = check_val('pos')
            if pos_check[0] is not None:
                self._set_pos(pos_check[0])
                return self.send_status()

            return print_error(pos_check[1])

        if msg_type == 'fix': # fix individual blind
            # partially move blind -- NO BOUNDS CHECKING!

            # pct_dir = check_pct_and_dir()
            # if pct_dir[0] is None:
            #     return print_error(pct_dir[1])

            # win_check = check_win()
            # if win_check is None:
            #     return print_error(win_check[1])

            # return self.move_single_blind(
            #     win_check[0], pct_dir[1], pct_dir[0]
            # )

            chk_pct = check_val('pct')
            if chk_pct[0] is None:
                return print_error(chk_pct[1])

            chk_dir = 'open' if chk_pct[0] >= 0 else 'close'

            chk_win = check_win()
            if chk_win[0] is None:
                return print_error(chk_win[1])

            return self.move_single_blind(
                chk_win[0], chk_dir, abs(chk_pct[0])
            )

        if msg_type == 'stat':
            return self.send_status()

        # if msg_type == 'transfer':
        #     self._rtcmem_handler.write_rtc_info(msg_type)
        #     from machine import deepsleep
        #     msecs = 3 * 1000
        #     print('Switching to file transfer socket server.')
        #     print('Connect to %s port %d with transfer client' % (config.ESP_IP, config.XFER_PORT))
        #     print('Calling machine.deepsleep(%d)' % msecs)
        #     deepsleep(msecs)

        return print_error()

    def loop(self):
        """Main loop"""
        ticks = ticks_ms()
        configure_time(tz=config.TZ, use_dst=config.DST)

        while True:
            new_msg = self.mqtt_handler.fetch_message()
            while new_msg is not None:
                self.handle_msg(new_msg)
                self.mqtt_handler.clear_read_message()
                new_msg = self.mqtt_handler.fetch_message()

            ticks_now = ticks_ms()

            if ticks_diff(ticks_now, ticks) > (60 * 60 * 1000):
                configure_time(tz=config.TZ, use_dst=config.DST)
                ticks = ticks_now

            self._send_heartbeat()

            sleep(5)
