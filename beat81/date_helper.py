from datetime import datetime, timedelta, date
from enum import Enum
from zoneinfo import ZoneInfo

class DaysOfWeek(Enum):
    monday = ["Monday", 0]
    tuesday = ["Tuesday", 1]
    wednesday = ["Wednesday", 2]
    thursday = ["Thursday", 3]
    friday = ["Friday", 4]
    saturday = ["Saturday", 5]
    sunday = ["Sunday", 6]


def get_date_formatted_day_hour(iso_date):
    date_begin = get_date_cet(iso_date)
    return date_begin.strftime("%A %d %b %-I:%M %p")

def get_date_formatted_hour(iso_date):
    date_begin = get_date_cet(iso_date)
    return date_begin.strftime("%H:%M")

def get_date_cet(iso_date):
    date_begin_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=ZoneInfo("UTC"))
    return date_begin_utc.astimezone(ZoneInfo("Europe/Berlin"))

def next_date_to_day(day_of_week):
    current_date = date.today()
    current_day_idx = current_date.weekday()
    target_day_idx = day_of_week.value[1]

    days_ahead = (target_day_idx - current_day_idx + 7) % 7
    if days_ahead == 0:
        days_ahead = 7  # If today is the target day, take the next week's day

    # Calculate the next date
    next_date = current_date + timedelta(days=days_ahead)

    return next_date

