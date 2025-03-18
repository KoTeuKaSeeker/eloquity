import requests

BASE_URL = "http://127.0.0.1:8001"  # Update if using a different host/port

# Replace with an actual task_id from your system
task_id = "d2c5fc5a-cf59-44e5-a1e9-cc2ae5fa0782"

# New status to update
status_data = {"status": "In Progress"}

# Send POST request
response = requests.post(f"{BASE_URL}/task/{task_id}/update_status", params=status_data)

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
