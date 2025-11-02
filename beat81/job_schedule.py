from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from beat81.beat81_api import register_recursive, find_next_event
from beat81.city_helper import City
from beat81.date_helper import DaysOfWeek, next_date_time_weekday
from beat81.db_helper import get_all_subscriptions


def job():
    subscriptions = get_all_subscriptions()
    for subscription in subscriptions:
        telegram_user_id = subscription[2]
        location_id = subscription[3]
        city = City[subscription[4]]
        day_of_week = DaysOfWeek[subscription[5]]
        time = subscription[6]
        hour = time.split(":")[0]
        minute = time.split(":")[1]
        next_date = next_date_time_weekday(day_of_week, int(hour), int(minute))
        next_event = find_next_event(city, location_id, next_date)
        register_recursive(next_event.get('id'), telegram_user_id, city, location_id, next_date)


def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, CronTrigger(hour="0", minute="5"))
    scheduler.start()
