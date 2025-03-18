import requests

file_path = "data/test_audio_data/audio_1.wav"
url = "http://localhost:8000/process_audio/"

with open(file_path, "rb") as f:
    files = {"file": ("audio_1.wav", f, "audio/mpeg")}
    response = requests.post(url, files=files)

print(response.json())
