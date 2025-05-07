import requests as rq
import time
import random
import string


class AuthenticatedSession(rq.Session):
    exceptions = rq.exceptions

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def get_authorization_token(self):
        def generate_unique_key():
            # Get current timestamp in milliseconds
            timestamp = int(time.time() * 1000)

            # Generate random alphanumeric string (6 characters)
            random_chars = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=6)
            )

            # Combine them together without any separator
            result = f"{timestamp}{random_chars}"

            return result

        # Generate a unique key
        uniquekey = generate_unique_key()

        # API endpoint
        url = "https://apexonline.lk/api/v1/user/login"

        # Set up headers
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Set up data
        data = {
            "password": self.password,
            "uniquekey": uniquekey,
            "username": self.username,
            "step": 3,
        }

        # Make the request
        response = rq.post(url, headers=headers, data=data)

        # Return the response
        return response

    def request(self, method, url, *args, **kwargs):
        response = self.get_authorization_token()
        if response.status_code == 200:
            auth_token = response.json()["body"]["token"]
        else:
            raise Exception("Login failed")

        # Ensure headers exist
        headers = kwargs.get("headers", {})
        headers.update({"Authorization": f"Bearer {auth_token}"})
        kwargs["headers"] = headers

        return super().request(method, url, *args, **kwargs)


requests = AuthenticatedSession("", "")


def generate_unique_key():
    # Get current timestamp in milliseconds
    timestamp = int(time.time() * 1000)

    # Generate random alphanumeric string (6 characters)
    random_chars = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=6)
    )

    # Combine them together without any separator
    result = f"{timestamp}{random_chars}"

    return result
