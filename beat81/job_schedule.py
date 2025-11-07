from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import utc
from beat81.beat81_api import register_recursive, find_next_event
from beat81.city_helper import City
from beat81.date_helper import DaysOfWeek, next_date_time_weekday
from beat81.db_helper import get_all_subscriptions


def job():
    print("Running job to register all subscriptions....")
    subscriptions = get_all_subscriptions()
    for subscription in subscriptions:
        telegram_user_id = subscription.get('telegram_user_id')
        location_id = subscription.get('location_id')
        city = City[subscription.get('city')]
        day_of_week = DaysOfWeek[subscription.get('day_of_week')]
        time = subscription.get('time')
        hour = time.split(":")[0]
        minute = time.split(":")[1]
        next_date = next_date_time_weekday(day_of_week, int(hour), int(minute))
        next_event = find_next_event(city, location_id, next_date)
        register_recursive(next_event.get('id'), telegram_user_id, city, location_id, next_date)


def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, CronTrigger(hour="22", minute="15", second="0"))
    scheduler.start()
