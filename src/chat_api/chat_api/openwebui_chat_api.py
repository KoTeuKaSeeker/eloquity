from typing import Dict, List, Callable
from src.chat_api.chat_api.chat_api_interface import ChatApiInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.file_containers.path_file_container import PathFileContainer
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File, UploadFile
from src.chat_api.chat.openwebui_chat import OpenWebUIChat
import asyncio
import requests
import uvicorn
import shutil
import os
import uuid
import datetime


class OpenwebuiChatApi():
    openwebui_coordinator_url: str
    handler_states: Dict[str, List[MessageHandler]]
    user_data_dicts: Dict[int, dict]
    user_active_states: Dict[int, str]
    user_active_task: Dict[int, dict]
    temp_path: str

    def __init__(self, openwebui_coordinator_url: str, temp_path: str):
        self.openwebui_coordinator_url = openwebui_coordinator_url
        self.handler_states = {}
        self.user_data_dicts = {}
        self.user_active_states = {}
        self.user_active_task = {}
        self.temp_path = temp_path 
        
    def set_handler_states(self, handler_states: Dict[str, List[MessageHandler]]):
        self.handler_states = handler_states

    def get_message_dict(self, task: dict):
        message = {}
        if len(task["initial_files"]) > 0:
            file_url = task["initial_files"][0]
            response = requests.get(file_url)

            file_name = str(uuid.uuid4())
            file_extension = os.path.splitext(file_url)[1]
            file_path = os.path.join(self.temp_path, file_name, file_extension)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            message["audio_container"] = PathFileContainer(file_path)

                
        if len(task["initial_message"]) > 0: message["text"] = task["initial_message"]
        message["forward_origin_date"] = datetime.datetime.now()
        message["date"] = datetime.datetime.now()

        return message
    
    def get_context_dict(self, task: dict):
        user_id = task["user_id"]

        context = {}
        context["user_id"] = user_id
        
        if user_id not in self.user_data_dicts:
            self.user_data_dicts[user_id] = {}
        context["user_data"] = self.user_data_dicts[user_id]

        return context
            
    def filter_handlers(self, handlers: List[MessageHandler], message: dict):
        for handler in handlers:
            message_filter = handler.get_message_filter()
            if message_filter.filter(message):
                return handler

    async def handle_user_task(self, task: dict):
        user_id = task["user_id"]

        message = self.get_message_dict(task)
        context = self.get_context_dict(task)
        chat = OpenWebUIChat(task, self.openwebui_coordinator_url)

        
        if user_id not in self.user_active_states:
            self.user_active_states[user_id] = "entry_point"

        active_state = self.user_active_states[user_id]
        handlers = self.handler_states[active_state]
        
        filtered_handler = self.filter_handlers(handlers, message)
        new_state = filtered_handler.get_message_handler()(message, context, chat)

        self.user_active_states[user_id] = new_state
        self.user_active_task[user_id] = None

    async def polling_loop(self, poll_interval: int = 3):
        while True:
            response = requests.get(self.openwebui_coordinator_url + "tasks/0")
            data = response.json()

            pending_tasks = [task for task in data["tasks"] if task["status"] == "pending"]
            for task in pending_tasks:
                user_id = task["user_id"]
                if user_id not in self.user_active_task:
                    self.user_active_task[user_id] = None
                
                user_task = self.user_active_task[user_id]
                if user_task != None:
                    continue
                
                self.user_active_task[user_id] = task
                asyncio.create_task(self.handle_user_task(task))
            await asyncio.sleep(poll_interval)

    def start(self, poll_interval: int = 3):
        asyncio.run(self.polling_loop(poll_interval))