import requests

BASE_URL = "http://127.0.0.1:8001"  # Update if using a different host/port

# Replace with an actual task_id from your system
task_id = "91098833-0064-4d11-939d-c86d3ba78845"

# New status to update
status_data = {"status": "Done"}

# Send POST request
response = requests.post(f"{BASE_URL}/task/{task_id}/update_status", params=status_data)

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
