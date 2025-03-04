from dataclasses import dataclass
from src.bitrix.task_container_interface import TaskContainerInterface

class BitrixUser():
    tasks_container: TaskContainerInterface
    id: int = -1
    name: str = ""
    last_name: str = ""
    second_name: str = ""
    email: str = ""
    personal_city: str = ""
    personal_mailbox: str = ""
    work_position: str = ""
    work_department: str = ""
    telegram_url: str = ""
    user_type: str = "employee"

    def __init__(self, tasks_container: TaskContainerInterface, id: int = -1, name: str = "", last_name: str = "", second_name: str = "", email: str = "", personal_city: str = "",
                 personal_mailbox: str = "", work_position: str = "", work_department: str = "", telegram_url: str = "", user_type: str = "employee"):
        self.tasks_container = tasks_container
        self.id = id
        self.name = name
        self.last_name = last_name
        self.second_name = second_name
        self.email = email
        self.personal_city = personal_city
        self.personal_mailbox = personal_mailbox
        self.work_position = work_position
        self.work_department = work_department
        self.telegram_url = telegram_url
        self.user_type = user_type
    
    def get_tasks(self):
        tasks = self.tasks_container.find_tasks(self.id)
        return tasks
    
    def __str__(self):
        return f"ФИО: {self.last_name} {self.name} {self.second_name}\nПочта: {self.email}/{self.personal_mailbox}\nДолжность: {self.work_position}"