import requests


api_url = "https://gptunnel.ru/v1/models"
headers = {
            "Authorization": "shds-748HxUWzKXVwSToCnkVp3opLXFC",
            "Content-Type": "application/json"
        }
response = requests.get(api_url, headers=headers)

print(response.json())

# deepseek-3
# deepseek-r1
# qwen-2.5-72b-instruct
# llama-3.1-405b