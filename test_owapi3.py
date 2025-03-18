import requests

BASE_URL = "http://127.0.0.1:8001"  # Update if using a different host/port

# Replace with an actual task_id from your system
task_id = "bb1e5d29-643f-4133-bb19-7d4658710dcf0"

# Message to add
message_data = {"message": "This is another message"}

# Send POST request
response = requests.post(f"{BASE_URL}/task/{task_id}/add_message", params=message_data)

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
