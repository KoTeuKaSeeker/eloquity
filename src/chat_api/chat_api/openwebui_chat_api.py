from typing import Dict, List
# from src.chat_api.chat_api.chat_api_interface import ChatApiInterface
# from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI
import uvicorn
import shutil
import os


class OpenwebuiChatApi():

    def __init__(self, app: FastAPI):
        self.app = app
        
    # def set_handler_states(self, handler_states: Dict[str, List[MessageHandlerInterface]]):
    def set_handler_states(self, handler_states: Dict[str, list]):
        pass

    

    def start(self, poll_interval: int = 3):
        uvicorn.run(self.app, host="0.0.0.0", port=8001, reload=True)