import random
import secrets
import string

import requests
import json

from data_store import createtestdata
from test.batinfo import UPowerManager

API_URL = 'http://127.0.0.1:5000/api/'  # Replace with your server URL if hosted
API_KEY = '94c417af3f4c91d851daacb07d59bcdf176b3a16e57c816d57de119308dee10a'       # Replace with actual API key

class Client:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.headers =  {'Content-Type': 'application/json'}

    def send_bat_data(self, data):
        data_payload = [
            data
        ]

        payload = {
            'api_key': API_KEY,
            'content': data_payload
        }

        return requests.post(f"{API_URL}battery", json=payload, headers=self.headers)

    def send_data(self, data):
        data_payload = [
            data
        ]

        payload = {
            'api_key': API_KEY,
            'content': data_payload
        }

        return requests.post(API_URL, json=payload, headers=self.headers)


def random_data(c):
    def generate_serial(length=16):
        characters = string.ascii_uppercase + string.digits  # Only uppercase letters and numbers
        serial = ''.join(secrets.choice(characters) for _ in range(length))
        return serial

    # Example: Generate 5 serials
    for _ in range(32):
        new_data = createtestdata().copy()
        new_data["Specs"]["Serial"] = generate_serial()
        for i in range(random.randint(1, 15)):
            response = c.send_data(new_data)
            print(f'Status Code: {response.status_code}')
            try:
                print('Response:', response.json())
            except Exception as e:
                print('Could not parse JSON response:', response.text)


if __name__ == "__main__":
    client = Client(API_URL, API_KEY)
    upower = UPowerManager()
    #random_data(client)