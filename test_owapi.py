import requests

url = "http://127.0.0.1:8001/send_message_to_query/"
data = {"message": "Hello"}

response = requests.post(url, data=data)

if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Request failed with status code:", response.status_code)
