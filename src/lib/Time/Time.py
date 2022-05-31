import datetime


class Time():
    
    @staticmethod
    def time_until_tomorrow():
        now = datetime.datetime.now()
        today = datetime.datetime.strftime(now, "%Y-%m-%d")
        today = datetime.datetime.strptime(today, "%Y-%m-%d")
        
        tomorrow = today + datetime.timedelta(days=1)
        
        delta = datetime.timedelta.total_seconds(tomorrow - now)
        delta = datetime.datetime.utcfromtimestamp(delta)
        delta = datetime.datetime.strftime(delta, "%H:%M:%S")
        
        return delta
