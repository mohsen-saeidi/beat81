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
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            token TEXT
        )
        ''')
        conn.commit()  # Save changes


# Function to save a user email and password
def save_user(email, password, token):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (email, password, token)
            VALUES (?, ?, ?)
            ''', (email, password, token))
            conn.commit()  # Save changes
            print(f"User {email} saved successfully.")
            return True
    except sqlite3.IntegrityError:
        # If the email already exists
        print(f"User {email} already exists in the database.")
        return False


# Function to get all saved users (optional, for debugging)
def get_all_users():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email, password, token FROM users')
        users = cursor.fetchall()
        return users