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
import pytz


class OpenwebuiChatApi():
    openwebui_coordinator_url: str
    handler_states: Dict[str, List[MessageHandler]]
    chat_data_dicts: Dict[int, dict]
    user_data_dicts: Dict[int, dict]
    user_active_states: Dict[str, str]
    user_active_task: Dict[str, dict]
    temp_path: str

    def __init__(self, openwebui_coordinator_url: str, temp_path: str):
        self.openwebui_coordinator_url = openwebui_coordinator_url
        self.handler_states = {}
        self.chat_data_dicts = {}
        self.user_data_dicts = {}
        self.user_active_states = {}
        self.user_active_task = {}
        self.temp_path = temp_path 
        
    def set_handler_states(self, handler_states: Dict[str, List[MessageHandler]]):
        self.handler_states = handler_states
    
    def get_data_key(self, task: dict, use_model_name: bool = True):
        model_key = f"-{task['model_name']}" if use_model_name else ""
        return f"{task['user_id']}-{task['chat_id']}{model_key}"

    def get_message_dict(self, task: dict):
        message = {}
        if len(task["initial_file"]) > 0:
            file_url = task["initial_file"]
            response = requests.get(file_url)

            file_name = str(uuid.uuid4())
            file_extension = os.path.splitext(file_url)[1]
            file_path = os.path.join(self.temp_path, file_name + file_extension)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            message["audio_container"] = PathFileContainer(file_path)

                
        if len(task["initial_message"]) > 0: message["text"] = task["initial_message"]
        message["forward_origin_date"] = datetime.datetime.now(pytz.UTC)
        message["date"] = datetime.datetime.now(pytz.UTC)

        return message
    
    def get_context_dict(self, task: dict):
        data_key = self.get_data_key(task)

        context = {}
        context["user_id"] = task['user_id']
        context["chat_id"] = task['chat_id']
        
        if data_key not in self.chat_data_dicts: self.chat_data_dicts[data_key] = {}
        if task['user_id'] not in self.user_data_dicts: self.user_data_dicts[task['user_id']] = {} 
        
        context["user_data"] = self.user_data_dicts[task['user_id']]
        context["chat_data"] = self.chat_data_dicts[data_key]
        context["chat_data"]["model_name"] = task['model_name']

        return context
            
    def filter_handlers(self, handlers: List[MessageHandler], message: dict):
        filtered_handler = None
        for handler in handlers:
            message_filter = handler.get_message_filter()
            if message_filter.filter(message):
                filtered_handler = handler
                break
        return filtered_handler

    def update_task_status(self, task_id: str, status: str):
        status_data = {"status": status}
        response = requests.post(f"{self.openwebui_coordinator_url}/task/{task_id}/update_status", params=status_data)

    async def handle_user_task(self, task: dict):
        data_key = self.get_data_key(task)

        message = self.get_message_dict(task)
        context = self.get_context_dict(task)
        chat = OpenWebUIChat(task, self.openwebui_coordinator_url)

        if data_key not in self.user_active_states:
            self.user_active_states[data_key] = "entry_point"

        active_state = self.user_active_states[data_key]

        state_handlers = self.handler_states[active_state]
        before_handlers = self.handler_states["global_state_before"] if "global_state_before" in self.handler_states else []
        after_handlers = self.handler_states["global_state_after"] if "global_state_after" in self.handler_states else []
        handlers = before_handlers + state_handlers + after_handlers
        
        filtered_handler = self.filter_handlers(handlers, message)
        new_state = active_state
        if filtered_handler is not None:
            new_state = await filtered_handler.get_message_handler()(message, context, chat)

        self.user_active_states[data_key] = new_state
        self.user_active_task[data_key] = None
        self.update_task_status(task["task_id"], "Done")
        

    async def polling_loop(self, poll_interval: float = 3):
        while True:
            response = requests.get(self.openwebui_coordinator_url + "tasks")
            data = response.json()

            pending_tasks = [task for task in data["tasks"] if task["status"] == "Pending"]
            for task in pending_tasks:
                data_key = self.get_data_key(task)
                if data_key not in self.user_active_task:
                    self.user_active_task[data_key] = None
                
                user_task = self.user_active_task[data_key]
                if user_task != None:
                    continue
                
                self.user_active_task[data_key] = task
                asyncio.create_task(self.handle_user_task(task))
            await asyncio.sleep(poll_interval)

    def start(self, poll_interval: float = 3):
        asyncio.run(self.polling_loop(poll_interval))