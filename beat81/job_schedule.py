from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from beat81.beat81_api import register_recursive, find_next_event, ticket_book
from beat81.city_helper import City
from beat81.date_helper import DaysOfWeek, next_date_time_weekday
from beat81.db_helper import get_all_subscriptions, get_all_auto_joins, cancel_auto_join


def subscription_job():
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
        date = next_date_time_weekday(day_of_week, int(hour), int(minute)) + timedelta(days=7)
        next_event = find_next_event(city, location_id, date)
        register_recursive(next_event.get('id'), telegram_user_id, city, location_id, date)


def auto_join_job():
    auto_joins = get_all_auto_joins()
    for auto_join in auto_joins:
        telegram_user_id = auto_join.get('telegram_user_id')
        ticket_id = auto_join.get('ticket_id')
        result = ticket_book(telegram_user_id, ticket_id)
        if result:
            print(f"Auto join booked successfully for ticket id {auto_join.get('ticket_id')}")
            cancel_auto_join(auto_join.get('id'))


def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(subscription_job, CronTrigger(hour="21", minute="0", second="0"))
    scheduler.add_job(auto_join_job, CronTrigger(minute="*/1", second="0"))
    scheduler.start()
