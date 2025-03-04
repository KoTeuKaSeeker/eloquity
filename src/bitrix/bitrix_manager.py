import requests
from typing import List
from src.bitrix.bitrix_user import BitrixUser
from src.bitrix.bitrix_task import BitrixTask
from src.bitrix.task_container_interface import TaskContainerInterface

class BitrixManager(TaskContainerInterface):
    webhook_url: str

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def find_users(self, last_name: str = None, name: str = None, second_name: str = None, user_id: int = -1, count_return_entries: int = 50) -> List[BitrixUser]:
        params = {}
        
        if last_name: params["FILTER[LAST_NAME]"] = last_name
        if name: params["FILTER[NAME]"] = name
        if second_name: params["FILTER[SECOND_NAME]"] = second_name
        if user_id >= 0: params["FILTER[ID]"] = user_id

        USER_GET_URL = f"{self.webhook_url}user.get"
        
        
        all_users = []
        start_point = 0
        while True:
            params["start"] = start_point
            response = requests.get(USER_GET_URL, params=params)
            data = response.json()

            if "result" not in data:
                break

            users = data["result"]
            all_users.extend(users) 

            if len(users) < 50 or (count_return_entries >= 0 and len(all_users) >= count_return_entries):
                break

            start_point += 50

        if count_return_entries >= 0:
            all_users = all_users[:count_return_entries]

        bitrix_users: List[BitrixUser] = []
        for user in all_users:
            bitrix_user = BitrixUser(
                self,
                int(user["ID"]),
                user["NAME"] if "NAME" in user else "",
                user["LAST_NAME"] if "LAST_NAME" in user else "",
                user["SECOND_NAME"] if "SECOND_NAME" in user else "",
                user["EMAIL"] if "EMAIL" in user else "",
                user["PERSONAL_CITY"] if "PERSONAL_CITY" in user else "",
                user["PERSONAL_MAILBOX"] if "PERSONAL_MAILBOX" in user else "",
                user["WORK_POSITION"] if "WORK_POSITION" in user else "",
                user["WORK_DEPARTMENT"] if "WORK_DEPARTMENT" in user else "",
                user["UF_USR_1667818345005"] if "UF_USR_1667818345005" in user else "",
                user["USER_TYPE"],
            )

            bitrix_users.append(bitrix_user)

        return bitrix_users

    def find_tasks(self, responsible_id: int = -1, task_id: int = -1, created_by_id: int = -1) -> List[BitrixTask]:
        filter = {}
        if responsible_id >= 0: filter["RESPONSIBLE_ID"] = responsible_id
        if task_id >= 0: filter["ID"] = task_id
        if created_by_id >= 0: filter["CREATED_BY"] = created_by_id

        params = {
            "filter": filter,
            "select": ["ID", "TITLE", "STATUS", "PRIORITY", "CREATED_BY", "DESCRIPTION"]
        }

        TASK_LIST_URL = f"{self.webhook_url}tasks.task.list"

        response = requests.post(TASK_LIST_URL, json=params)
        tasks = response.json()["result"]["tasks"]
        
        bitrix_tasks: List[BitrixTask] = []
        for task in tasks:
            bitrix_task = BitrixTask(int(task["id"]), task["title"], int(task["createdBy"]), responsible_id, int(task["status"]), int(task["priority"]), task["description"])
            
            bitrix_tasks.append(bitrix_task)

        return bitrix_tasks

    def create_task_on_bitrix(self, task: BitrixTask):
        TASK_ADD_URL = f"{self.webhook_url}tasks.task.add"

        task_data = {
            "fields": {
                "TITLE": task.title,
                "DESCRIPTION": task.discription,
                "RESPONSIBLE_ID": task.responsible_id,
                "CREATED_BY": task.created_by_id,
                "DEADLINE": task.deadline,
                "PRIORITY": task.priority,
            }
        }

        response = requests.post(TASK_ADD_URL, json=task_data)
        return response
    
    def delete_task_on_bitrix(self, task: BitrixTask):
        TASK_DELETE_URL = f"{self.webhook_url}tasks.task.delete"

        data = {"taskId": task.id}

        response = requests.post(TASK_DELETE_URL, json=data)
        return response.json()
    
