import requests

BASE_URL = "http://127.0.0.1:8001"  # Update if using a different host/port

# Replace with an actual task_id from your system
task_id = "91098833-0064-4d11-939d-c86d3ba78845"

# Message to add
message_data = {"message": "bbbbbbbbbbbbbbbbbbb"}

# Send POST request
response = requests.post(f"{BASE_URL}/task/{task_id}/add_message", params=message_data)

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
