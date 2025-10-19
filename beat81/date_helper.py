from datetime import datetime
from zoneinfo import ZoneInfo

def get_date_formatted_short(iso_date):
    date_begin = get_date_cet(iso_date)
    return date_begin.strftime("%A %d %b %-I:%M %p")

def get_date_cet(iso_date):
    date_begin_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=ZoneInfo("UTC"))
    return date_begin_utc.astimezone(ZoneInfo("Europe/Berlin"))
