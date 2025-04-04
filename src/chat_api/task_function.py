from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from src.chat_api.chat.chat_interface import ChatInterface

class TaskFunction():
    handler_function: Callable[[dict, dict, "ChatInterface"], str]
    message: dict
    context: dict 
    chat: "ChatInterface"

    def __init__(self, 
                 handler_function: Callable[[dict, dict, "ChatInterface"], str], 
                 message: dict, 
                 context: dict, 
                 chat: "ChatInterface"):
        self.handler_function = handler_function
        self.message = message
        self.context = context
        self.chat = chat
