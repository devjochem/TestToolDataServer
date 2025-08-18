import requests
import json

from data_store import createtestdata

API_URL = 'http://127.0.0.1:5000/api/data'  # Replace with your server URL if hosted
API_KEY = 'b55324f1fb6d88d29b655f69a4c077e4'         # Replace with actual API key

data_payload = [
    createtestdata()
]

payload = {
    'api_key': API_KEY,
    'content': data_payload
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(API_URL, json=payload, headers=headers)

print(f'Status Code: {response.status_code}')
try:
    print('Response:', response.json())
except Exception as e:
    print('Could not parse JSON response:', response.text)
