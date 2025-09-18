import time
import datetime


class AdvTime():
    
    def __init__(self, set_time = None):
        if set_time:
            self._time = set_time
        else:
            self._time = time.time()
    
    def get_time_s(self):
        return self._time
    
    def get_time(self, unit = 'seconds'):
        if unit == 'seconds':
            return self.get_time_s()
        elif unit == 'minutes':
            return self.get_time_s() / 60
        elif unit == 'hours':
            return self.get_time_s() / 3600
        else:
            return 'not yed defined'
    
    def get_time_date(self):
        return AdvTime.get_formated_time('%Y-%m-%d %H:%M:%S', self.get_time_s(), False)
    
    def get_time_formated(self, format):
        return AdvTime.get_formated_time(format, self.get_time_s(), False)
    
    def get_time_until_tomorrow(self):
        now   = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        tomorrow = today + datetime.timedelta(1)
        
        return tomorrow.timestamp() - self._time

    @staticmethod
    def get_formated_time(format_string, s, local = True):
        '''
            format_string: the output format
            s: time in seconds
            local: Boolean, if ture localtime, if false gmtime
        '''
        if local:
            return time.strftime(format_string, time.localtime(s))
        else:
            return time.strftime(format_string, time.gmtime(s))

    @staticmethod
    def get_delta_time(format_string, t1_s, t2_s):
        delta = t2_s - t1_s
        return AdvTime.get_formated_time(format_string, delta, False)