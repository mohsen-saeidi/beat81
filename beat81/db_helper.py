import os
import sqlite3
from datetime import datetime

DATA_DIRECTORY = "data"
DATABASE_FILE = os.path.join(DATA_DIRECTORY, "user_data.db")

if not os.path.exists(DATA_DIRECTORY):
    os.makedirs(DATA_DIRECTORY)


def init_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id TEXT NOT NULL UNIQUE,
                beat81_user_id TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                token TEXT,
                first_name TEXT,
                last_name TEXT,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login_date DATETIME,
                UNIQUE (telegram_user_id, beat81_user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                telegram_user_id TEXT NOT NULL,
                location_id TEXT NOT NULL,
                city TEXT NOT NULL,
                day_of_week TEXT NOT NULL,
                time TEXT NOT NULL,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE (user_id, location_id, day_of_week, time)
            )
        ''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS autojoins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    telegram_user_id TEXT NOT NULL,
                    ticket_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE (user_id, event_id)
                )
        ''')

        conn.commit()


def save_user(telegram_user_id, beat81_user_id, email, token, first_name, last_name, creation_time=datetime.now(),
              last_login_date=datetime.now()):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (telegram_user_id, beat81_user_id, email, token, first_name, last_name, creation_time, last_login_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_user_id) DO UPDATE SET
                    beat81_user_id = excluded.beat81_user_id,
                    email = excluded.email,
                    token = excluded.token,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    last_login_date = excluded.last_login_date
            ''', (
                telegram_user_id, beat81_user_id, email, token, first_name, last_name, creation_time, last_login_date))
            conn.commit()
            print(f"User {email} saved successfully.")
            return True
    except sqlite3.IntegrityError:
        print(f"User {email} already exists in the database.")
        return False


def save_subscription(telegram_user_id, location_id, city, day_of_week, time, creation_time=datetime.now()):
    user = get_user_by_user_id(telegram_user_id)
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO subscriptions (user_id, telegram_user_id, location_id, city, day_of_week, time, creation_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user['id'], telegram_user_id, location_id, city.name, day_of_week, time, creation_time))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        print(f"Subscription {user['id']}, {location_id}, {day_of_week}, {time} already exists in the database.")
        return False


def save_auto_join(telegram_user_id, ticket_id, event_id, creation_time=datetime.now()):
    user = get_user_by_user_id(telegram_user_id)
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO autojoins (user_id, telegram_user_id, ticket_id, event_id, creation_time)
            VALUES (?, ?, ?, ?, ?)
            ''', (user['id'], telegram_user_id, ticket_id, event_id, creation_time))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        print(f"auto join {user['id']}, {ticket_id}, {event_id} already exists in the database.")
        return False


def get_user_by_email(email):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM users WHERE email = ?
            ''', (email,))

            return fetchone_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching user by email: {e}")
        return None


def get_user_by_user_id(telegram_user_id):
    telegram_user_id = str(telegram_user_id)
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM users WHERE telegram_user_id = ?
            ''', (telegram_user_id,))

            return fetchone_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching user by telegram_user_id: {telegram_user_id}, {e}")
        return None


def get_all_subscriptions():
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM subscriptions
            ''')

            return fetchall_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching subscriptions: {e}")
        return None


def get_all_auto_joins():
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM autojoins
            ''')

            return fetchall_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching auto joins: {e}")
        return None


def get_user_subscriptions(telegram_user_id):
    telegram_user_id = str(telegram_user_id)
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM subscriptions WHERE telegram_user_id = ?
            ''', (telegram_user_id,))

            return fetchall_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching user {telegram_user_id} subscriptions: {e}")
        return None


def get_user_auto_joins(telegram_user_id):
    telegram_user_id = str(telegram_user_id)
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM autojoins WHERE telegram_user_id = ?
            ''', (telegram_user_id,))

            return fetchall_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching user {telegram_user_id} auto joins: {e}")
        return None


def get_subscription_by_id(subscription_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM subscriptions WHERE id = ?
            ''', (subscription_id,))

            return fetchone_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching subscriptions: {subscription_id}, {e}")
        return None


def get_auto_join_by_id(auto_join_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM autojoins WHERE id = ?
            ''', (auto_join_id,))

            return fetchone_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching auto join: {auto_join_id}, {e}")
        return None


def get_auto_join_by_event_id(event_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT * FROM autojoins WHERE event_id = ?
            ''', (event_id,))

            return fetchone_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching autojoins: {e}")
        return None


def cancel_subscription(subscription_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM subscriptions WHERE id = ?', (subscription_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"An error occurred while cancelling subscription: {e}")
        return False


def cancel_auto_join(auto_join_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM autojoins WHERE id = ?', (auto_join_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"An error occurred while cancelling auto join: {e}")
        return False


def delete_auto_join_by_ticket_id(ticket_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM autojoins WHERE ticket_id = ?', (ticket_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"An error occurred while deleting auto join: {e}")
        return False


def clear_token(telegram_user_id):
    telegram_user_id = str(telegram_user_id)
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('Update users SET token = NULL WHERE telegram_user_id = ?', (telegram_user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"An error occurred while clearing token: {e}")
        return False


def fetchall_as_json(cursor):
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def fetchone_as_json(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))
