import requests
from src.bitrix.bitrix_manager import BitrixManager

WEBHOOK_URL = "https://portal.zebrains.team/rest/1508/824o8bx2f0471x1f/"

bitrix_manager = BitrixManager(WEBHOOK_URL)
users = bitrix_manager.find_users(count_return_entries=-1)

for user in users:
    print(f"{str(user)}\n")

user = bitrix_manager.find_users("Долгов", "Данил", "Петрович")[0]
tasks = user.get_tasks()