import requests

# The URL of the FastAPI endpoint
user_id = "234g23uy2g"  # The user_id to test with
url = f"http://localhost:8001/tasks"

# Send the GET request to the endpoint
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print("Tasks retrieved successfully:")
    print(response.json())  # Print the response data (list of tasks)
elif response.status_code == 404:
    print(f"No tasks found for user {user_id}.")
else:
    print(f"Failed to retrieve tasks. Status code: {response.status_code}")
