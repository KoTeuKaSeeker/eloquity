import requests

BASE_URL = "http://127.0.0.1:8001"  # Update if using a different host/port

# Replace with an actual task_id from your system
task_id = "f76948ec-28db-469a-86af-7994761d108d"

# Send GET request
response = requests.get(f"{BASE_URL}/task/{task_id}")

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
