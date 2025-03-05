from abc import ABC, abstractmethod
from typing import List
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext._handlers.basehandler import BaseHandler

class CommandInterface(ABC):
    @abstractmethod
    def get_telegram_handler(self) -> BaseHandler:
        pass