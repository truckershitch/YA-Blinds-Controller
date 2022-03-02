"""
Logs error from passed-in function to a file

Usage:
wrapper = ErrorWrapper(logfile)
def f(a, b, c)
wrapper.wrap(obj, fn_name, a, b, c=3)

Last update May 23, 2021
"""

class ErrorWrapper(object):
    """Main class"""
    def __init__(self, logfile):
        self._log = logfile

    def _exit(self):
        """Quit program"""
        import sys
        print('Calling exit()')
        sys.exit()

    def _restart(self, r_type='reset', msg=None, sleep_secs=5):
        """Restart  device"""
        from machine import reset, deepsleep
        if msg is not None:
            print(msg)
        if r_type == 'deepsleep': # save RTC memory
            print('Calling deepsleep() for %d seconds.' % sleep_secs)
            deepsleep(sleep_secs * 1000) # pylint: disable=too-many-function-args
        else:
            from utime import sleep
            print('Calling reset()')
            sleep(1)
            reset()

    def _log_error(self, err):
        """Log error to file"""
        import sys
        from utime import time
        from set_rtc import format_datetime
        with open(self._log, 'a') as file:
            file.write('%s UTC\n' % format_datetime(time()))
            sys.print_exception(err, file) # pylint: disable=no-member
            file.write('\n')
        print('\n*** Error:\n%s\nLogged to %s' % (err, self._log))

    def wrap(self, obj, fn_name, *args, **kwargs):
        """Handle error for fn"""
        output = None
        fn = getattr(obj, fn_name)

        try:
            if len(args) > 0:
                output = fn(*args, **kwargs)
            elif len(kwargs) > 0:
                output = fn(**kwargs)
            else:
                output = fn()

        except Exception as e:
            self._log_error(e)
            self._restart(
                r_type='reset',
                msg='Error: %s' % e
            )

        return output
