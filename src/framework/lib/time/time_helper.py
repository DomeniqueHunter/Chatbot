from datetime import datetime, timedelta, time


def days_hours_minutes(td:timedelta, seconds:bool=False) -> tuple:
    if seconds:
        return td.days, td.seconds // 3600, (td.seconds // 60) % 60, td.seconds % 60
    else:
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


def int_to_datetime_string(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def datetime_to_string(dt:datetime, fmt:str="%Y-%m-%d %H:%M:%S") -> str:
    return dt.strftime(fmt)


def time_remaining(duration:int) -> str:
    """
    duration in seconds
    """
    days = duration // 86400
    hours = duration // 3600 % 24
    minutes = duration // 60 % 60
    seconds = duration % 60

    units = ((days, "d"), (hours, "h"), (minutes, "min"), (seconds, "sec"))
    parts = [f"{value}{unit}" for value, unit in units if value]
    return " ".join(parts) or "0sec"

