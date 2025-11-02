import os
import sqlite3
from datetime import datetime

# Define the directory and file for the database
DATA_DIRECTORY = "data"
DATABASE_FILE = os.path.join(DATA_DIRECTORY, "user_data.db")

# Ensure the data directory exists
if not os.path.exists(DATA_DIRECTORY):
    os.makedirs(DATA_DIRECTORY)  # Create the data directory if it doesn't exist


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
                last_login_date DATETIME 
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
        conn.commit()  # Save changes


def save_user(telegram_user_id, beat81_user_id, email, token, first_name, last_name, creation_time=datetime.now(),
              last_login_date=datetime.now()):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (telegram_user_id, beat81_user_id, email, token, first_name, last_name, creation_time, last_login_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                telegram_user_id, beat81_user_id, email, token, first_name, last_name, creation_time, last_login_date))
            conn.commit()  # Save changes
            print(f"User {email} saved successfully.")
            return True
    except sqlite3.IntegrityError:
        # If the email already exists
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
            conn.commit()  # Save changes
            return True
    except sqlite3.IntegrityError:
        # If the email already exists
        print(f"Subscription {user['id']}, {location_id}, {day_of_week}, {time} already exists in the database.")
        return False


def get_user_by_email(email):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            # Query to fetch user details by email
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

            # Query to fetch user details by email
            cursor.execute('''
            SELECT * FROM users WHERE telegram_user_id = ?
            ''', (telegram_user_id,))

            return fetchone_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching user by telegram_user_id: {e}")
        return None


def get_all_subscriptions():
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            # Query to fetch user details by email
            cursor.execute('''
            SELECT * FROM subscriptions
            ''')

            return fetchall_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching subscriptions: {e}")
        return None


def get_user_subscriptions(telegram_user_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            # Query to fetch user details by email
            cursor.execute('''
            SELECT * FROM subscriptions WHERE telegram_user_id = ?
            ''', (telegram_user_id,))

            return fetchall_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching subscriptions: {e}")
        return None


def get_subscription_by_id(subscription_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            # Query to fetch user details by email
            cursor.execute('''
            SELECT * FROM subscriptions WHERE id = ?
            ''', subscription_id)

            return fetchone_as_json(cursor)

    except Exception as e:
        print(f"An error occurred while fetching subscriptions: {e}")
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


def clear_token(telegram_user_id):
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
        return None  # Return None if no more rows are found
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))
