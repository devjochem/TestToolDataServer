import random
import secrets
import string

import requests
import json

from batteryinfo import UPowerManager
from data_store import createtestdata
from tests.systeminfo import Specs

API_URL = 'http://127.0.0.1:5000/api/'  # Replace with your server URL if hosted
API_KEY = '9cd4c5e412f4df5908c48f7f3fe2274cb7c775bc98d80c1a86c401cb73aefc7e'       # Replace with actual API key

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
            'serial': Specs().getSerial(),
            'test_id': "test",
            'content': data_payload
        }

        return requests.post(f"{API_URL}battery", json=payload, headers=self.headers)

    def send_test_data(self, name, serial, specs, test_results):

        payload = {
            'api_key': API_KEY,
            'name': name,
            'serial_number':serial,
            'specs': specs,
            'test_results': test_results
        }

        return requests.post(f"{API_URL}results", json=payload, headers=self.headers)


def create_test_data(data):

    name = data['Naam']
    serial = data["Specs"]['Serial']
    specs = data['Specs']
    test_results = data['TestResults']

    return name,serial,[specs],[test_results]


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
            name,serial,specs,tests_results = create_test_data(new_data)
            print(name,serial,specs,tests_results)
            response = c.send_test_data(name,serial,specs,tests_results)
            print(f'Status Code: {response.status_code}')
            try:
                print('Response:', response.json())
            except Exception as e:
                print('Could not parse JSON response:', response.text)


if __name__ == "__main__":
    client = Client(API_URL, API_KEY)
    upower = UPowerManager()
    devices = upower.enumerate_devices()
    for device in devices:
        if "battery" in device.lower():
            print(upower.print_battery_info(device))
            client.send_bat_data(upower.print_battery_info(device))
    random_data(client)