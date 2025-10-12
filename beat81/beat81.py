from datetime import datetime

import jwt
import requests

from db_helper import init_db, save_user, get_user_by_user_id

init_db()


# API login function
def login(telegram_user_id, email, password):
    url = "https://api.production.b81.io/api/authentication"  # The login API URL
    payload = {
        "email": email,
        "password": password,
        "strategy": "local"
    }

    try:
        response = requests.post(url, json=payload)

        # Check if the API call was successful
        if response.status_code == 201:
            print("Login successful!")
            response_data = response.json()
            token = response_data.get("data", {}).get("accessToken")
            user_info = extract_data_from_jwt(token)

            if save_user(telegram_user_id=telegram_user_id, beat81_user_id=user_info['userId'], email=email,
                         password=password,
                         token=token, first_name=user_info['given_name'], last_name=user_info['family_name'],
                         creation_time=datetime.now(), last_login_date=datetime.now()):
                print(f"{email} saved to the database.")
            else:
                print(f"{email} already exists in the database.")

            return True
        elif response.status_code == 401:
            print("Invalid credentials.")
            return False
        else:
            print(f"Unexpected response: {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error while calling the login API: {e}")
        return False


def tickets(telegram_user_id):
    user = get_user_by_user_id(str(telegram_user_id))

    url = "https://api.production.b81.io/api/tickets"

    # Prepare query parameters
    params = {}
    params["user_id"] = user['beat81_user_id']
    params["status_ne"] = 'cancelled'
    params["event_date_begin_gte"] = datetime.now()

    try:
        # Make the GET request to fetch tickets with optional filters
        headers = {"Authorization": f"Bearer {user['token']}"}
        response = requests.get(url, params=params, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            print("Tickets fetched successfully!")
            tickets_data = response.json()
            print(tickets_data)
            return tickets_data.get('total')  # Return the response data
        else:
            print(f"Failed to fetch tickets: {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error while calling the tickets API: {e}")
        return None


def extract_data_from_jwt(jwt_token, secret_key=None):
    try:
        # Decode the token
        if secret_key:
            # If the token is signed, provide the secret key
            decoded_data = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        else:
            # If the token is unsigned, decode without verification
            decoded_data = jwt.decode(jwt_token, options={"verify_signature": False})

        # Extract specific fields
        user_data = {
            "userId": decoded_data.get("userId"),
            "given_name": decoded_data.get("given_name"),
            "family_name": decoded_data.get("family_name"),
            "email": decoded_data.get("email")
        }
        return user_data

    except jwt.ExpiredSignatureError:
        print("The token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None
