"""Set RTC Clock"""
import sys
import gc
from time import sleep, time, localtime
import config_esp8266 as config

def set_ntp_time(ntp_servers):
    """Get time from NTP server"""
    import sntp # modified ntptime

    print('Now setting clock with NTP server', end='')
    time_is_set = False
    count = 0
    while not time_is_set:
        print('.', end='')
        time_is_set = sntp.settime(ntp_servers)
        if time_is_set:
            print('Set time successfully.')
        sleep(1)
        count += 1
        if count == 5:
            print('Could not connect to NTP Server!')
            with open(config.ERROR_FILE, 'a') as file:
                file.write('%s UTC\n' % format_datetime(time()))
                file.write('Could not connect to NTP Server\n')

    del sys.modules['sntp']
    gc.collect()

def check_for_summer_time(timestamp, country='US'):
    """Adjust time for DST"""
    import dst

    (curr_dst_status,
     adj_timestamp)    = dst.SummerTimeAdjustment(timestamp, country)

    del sys.modules['dst']
    gc.collect()

    return curr_dst_status, adj_timestamp

def format_datetime(timestamp):
    """Make timestamp readable"""
    t = localtime(timestamp)
    fmt = '%02d/%02d/%04d %02d:%02d:%02d'
    return fmt % (t[1], t[2], t[0], t[3], t[4], t[5])

def configure_time(tz, use_dst):
    """Configure time, using DST if needed"""
    SECS_IN_HOUR = 3600

    set_ntp_time(config.NTP_SERVERS)
    timestamp = time() + tz * SECS_IN_HOUR
    if use_dst:
        curr_dst_status, adj_timestamp = check_for_summer_time(timestamp)

    print('Current UNIX timestamp: %d\nDST Status: %d\nDate & Time: %s'
          % (timestamp, curr_dst_status, format_datetime(adj_timestamp)))
