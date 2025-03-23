import requests

BASE_URL = "http://192.168.43.253:8001"  # Update this if your server is running elsewhere
task_id = "8f997470-7332-4705-b6a3-3836d31400e4"  # Replace with the task_id you want to test
file_path = "data/test_data/audio/audio_1.wav"  # Replace with the actual file path you want to upload

# Open the file to send it in the request
with open(file_path, "rb") as file:
    response = requests.post(
        f"{BASE_URL}/task/create",
        data={"user_id": "0", "message": "Some test message..."},
        files={"file": (file.name, file, "application/octet-stream")}
    )

# Print response details
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
