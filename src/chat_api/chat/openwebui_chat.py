from typing import Any
import asyncio
from src.chat_api.chat.chat_interface import ChatInterface
import requests

class OpenWebUIChat(ChatInterface):

    task: dict
    openwebui_coordinator_url: str

    def __init__(self, task: dict, openwebui_coordinator_url: str):
        self.task = task
        self.openwebui_coordinator_url = openwebui_coordinator_url

    async def send_message_to_query(self, message: str):
        task_id = self.task["task_id"]
        requests.post(self.openwebui_coordinator_url + f"task/{task_id}/add_message", params={"message": message})

    async def send_file_to_query(self, file_path: str):
        task_id = self.task["task_id"]
        with open(file_path, "rb") as file:
            response = requests.post(
                f"{self.openwebui_coordinator_url}/task/{task_id}/upload_file", 
                files={"file": (file.name, file, "application/octet-stream")}
            )
    
    async def send_message_to_event_loop(self, message: dict, context: dict, chat: ChatInterface):
        """
            Отправляет новое сообщение, которое должен увидеть сам же бот, но не пользователь (сам себе отправляет сообщение, которое поймают хендлеры).
            С помощью этой функции можно произвольно отправлять сообщеине другим хэндлерам, и, в дальнейшем, переходить на них.
        """
        message_text = message["text"] if "text" in message else ""

        def make_request(files: dict = {}):
            response = requests.post(
                    f"{self.openwebui_coordinator_url}/task/create",
                    data={"user_id": self.task["user_id"], "chat_id": self.task["chat_id"], "message": message_text},
                    files=files
                )

        if "audio_container" in message:
            file_path = await message["audio_container"].get_file_path()
            with open(file_path, "rb") as file:
                make_request({"file": (file.name, file, "application/octet-stream")})
        else:
            make_request()


    def get_entry_point_state(self) -> Any:
        """
            Возвращает значение, которое изменяет стейт машину в состояние entry_point. Эта функция сделана специальна, так как в случа telegram это 
            не просто строка, а переменная определённого типа (которая здесь в этом случае и должна вернуться). Если же такого особого функционала нет
            (как вероятнее всего и будет в OpenWebUI), то можно просто также и вернуть строку 'entry_point'.

        """
        return "entry_point"
