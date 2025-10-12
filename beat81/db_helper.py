import sqlite3
import os

# Define the directory and file for the database
DATA_DIRECTORY = "../data"
DATABASE_FILE = os.path.join(DATA_DIRECTORY, "user_data.db")

# Ensure the data directory exists
if not os.path.exists(DATA_DIRECTORY):
    os.makedirs(DATA_DIRECTORY)  # Create the data directory if it doesn't exist


# Function to initialize the database (create the table if it doesn't exist)
def init_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id TEXT NOT NULL UNIQUE,
            beat81_user_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            token TEXT,
            first_name TEXT,
            last_name TEXT,
            creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login_date TIMESTAMP 
        )
        ''')
        conn.commit()  # Save changes


# Function to save a user email and password
def save_user(telegram_user_id, beat81_user_id, email, password, token, first_name, last_name, creation_time, last_login_date):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (telegram_user_id, beat81_user_id, email, password, token, first_name, last_name, creation_time, last_login_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_user_id, beat81_user_id, email, password, token, first_name, last_name, creation_time, last_login_date))
            conn.commit()  # Save changes
            print(f"User {email} saved successfully.")
            return True
    except sqlite3.IntegrityError:
        # If the email already exists
        print(f"User {email} already exists in the database.")
        return False


def get_user_by_email(email):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            # Query to fetch user details by email
            cursor.execute('''
            SELECT *
            FROM users
            WHERE email = ?
            ''', (email,))

            user = cursor.fetchone()

            # Return the user record if it exists
            if user:
                return {
                    "id": user[0],
                    "telegram_user_id": user[1],
                    "beat81_user_id": user[2],
                    "email": user[3],
                    "password": user[4],
                    "token": user[5],
                    "first_name": user[6],
                    "last_name": user[7],
                    "creation_time": user[8],
                    "last_login_date": user[9]
                }
            else:
                print(f"No user found with email: {email}")
                return None
    except Exception as e:
        print(f"An error occurred while fetching user by email: {e}")
        return None

def get_user_by_user_id(user_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            # Query to fetch user details by email
            cursor.execute('''
            SELECT *
            FROM users
            WHERE telegram_user_id = ?
            ''', (user_id,))

            user = cursor.fetchone()

            # Return the user record if it exists
            if user:
                return {
                    "id": user[0],
                    "telegram_user_id": user[1],
                    "beat81_user_id": user[2],
                    "email": user[3],
                    "password": user[4],
                    "token": user[5],
                    "first_name": user[6],
                    "last_name": user[7],
                    "creation_time": user[8],
                    "last_login_date": user[9]
                }
            else:
                print(f"No user found with user_id: {user_id}")
                return None
    except Exception as e:
        print(f"An error occurred while fetching user by user_id: {e}")
        return None