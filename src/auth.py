import requests as rq
import time
import random
import string

from data_types import Config

config = Config()


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


class AuthenticatedSession(rq.Session):
    _auth_token = None
    exceptions = rq.exceptions

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def get_authorization_token(self):
        # Generate a unique key
        unique_key = generate_unique_key()

        # API endpoint
        url = "https://apexonline.lk/api/v1/user/login"

        # Set up headers
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Set up data
        data = {
            "password": self.password,
            "uniquekey": unique_key,
            "username": self.username,
            "step": 3,
        }

        # Make the request
        response = rq.post(url, headers=headers, data=data)

        # Return the response
        return response

    def update_auth_token(self):
        # Get the current time
        now = time.time()

        # Get the expiration time of the token
        expiration_time = getattr(self, "_expiration_time", 0)

        # If the token has expired, re authenticate
        if now > expiration_time:
            response = self.get_authorization_token()
            if response.status_code == 200:
                self._auth_token = response.json()["body"]["token"]
                self._expiration_time = now + 60 * 15  # expires in 15 minutes
            else:
                raise Exception("Login failed")

    def request(self, method, url, *args, **kwargs):
        self.update_auth_token()

        """ response = self.get_authorization_token()
        if response.status_code == 200:
            auth_token = response.json()['body']['token']
        else:
            raise Exception('Login failed') """

        # Ensure headers exist
        headers = kwargs.get("headers", {})
        headers.update({"Authorization": f"Bearer {self._auth_token}"})
        kwargs["headers"] = headers

        return super().request(method, url, *args, **kwargs)


auth_request = AuthenticatedSession(config.username, config.password)
