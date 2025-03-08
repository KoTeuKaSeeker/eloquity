from src.bitrix.bitrix_manager import BitrixManager
import requests

webhook_url = "https://portal.zebrains.team/rest/1508/824o8bx2f0471x1f/"

response = requests.get(webhook_url + "app.info")
data = response.json()
pass