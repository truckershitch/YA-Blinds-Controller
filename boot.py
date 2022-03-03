# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos
uos.dupterm(None, 1) # disable REPL on UART(0)
import sys
import gc
import webrepl
webrepl.start()
gc.collect()
del sys.path[0]
sys.path.append('')
from connect_wifi import connect
connect()
