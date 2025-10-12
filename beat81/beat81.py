import requests
from db_helper import init_db, save_user

init_db()


# API login function
def login(email, password):
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

            if save_user(email=email, password=password, token=token):
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
