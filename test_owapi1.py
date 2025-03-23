import requests

# The URL of the FastAPI endpoint
url = "http://localhost:8001/task/create"

# Data to send with the request
data = {
    "user_id": "0",
    "message": "A new era has come 2",
    "files": []
}

# Send the POST request to the endpoint
response = requests.post(url, json=data)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print("Task created successfully:")
    print(response.json())  # Print the response data
else:
    print(f"Failed to create task. Status code: {response.status_code}")
