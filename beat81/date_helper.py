from datetime import datetime
from zoneinfo import ZoneInfo

def get_date_formatted(iso_date):
    date_begin_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=ZoneInfo("UTC"))
    date_begin = date_begin_utc.astimezone(ZoneInfo("Europe/Berlin"))
    return date_begin.strftime("%A %d %b %-I:%M %p")