from datetime import datetime, timedelta, time


def days_hours_minutes(td):
    return td.days, td.seconds // 3600, (td.seconds // 60) % 60
   
        
def formatted_delta(dt:timedelta) -> str:
    days, hours, minutes = days_hours_minutes(dt)
    formatted_time = ""
    if days:
        formatted_time += f"{days}d "
    
    formatted_time += f"{hours}h {minutes}m"    
    
    return formatted_time


def time_until_tomorrow():
    now = datetime.now()
    tomorrow = datetime.combine(now.date() + timedelta(days=1), time.min)
    time_until_tomorrow = tomorrow - now
    
    # Extract hours and minutes
    hours, remainder = divmod(time_until_tomorrow.seconds, 3600)
    minutes = remainder // 60
    
    return f"{hours}h {minutes}m"



def test():
    print(time_until_tomorrow())
    print()
    
    
if __name__ == "__main__":
    test()
