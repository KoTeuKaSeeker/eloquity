import requests

BASE_URL = "http://127.0.0.1:8001"  # Update this if your server is running elsewhere
task_id = "d1ba6a82-c0a6-4cbc-9831-429759c13c2c"  # Replace with the task_id you want to test
file_path = "data/test_audio_data/audio_1.wav"  # Replace with the actual file path you want to upload

# Open the file to send it in the request
with open(file_path, "rb") as file:
    response = requests.post(
        f"{BASE_URL}/task/{task_id}/upload_file",
        files={"file": (file.name, file, "application/octet-stream")}
    )

# Print response details
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
