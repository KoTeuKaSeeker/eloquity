from typing import Any
from abc import ABC, abstractmethod
from chat_api.message_handlers.message_handler_interface import MessageHandlerInterface

class ChatInterface(ABC):
    @abstractmethod
    async def send_message_to_query(self, message: str):
        pass

    @abstractmethod
    async def send_file_to_query(self, file_path: str):
        pass        
    
    @abstractmethod
    async def send_message_to_event_loop(self, message: dict, context: dict, chat: "ChatInterface"):
        """
            Отправляет новое сообщение, которое должен увидеть сам же бот, но не пользователь (сам себе отправляет сообщение, которое поймают хендлеры).
            С помощью этой функции можно произвольно отправлять сообщеине другим хэндлерам, и, в дальнейшем, переходить на них.
        """
        pass

    @abstractmethod
    def get_entry_point_state(self) -> Any:
        """
            Возвращает значение, которое изменяет стейт машину в состояние entry_point. Эта функция сделана специальна, так как в случа telegram это 
            не просто строка, а переменная определённого типа (которая здесь в этом случае и должна вернуться). Если же такого особого функционала нет
            (как вероятнее всего и будет в OpenWebUI), то можно просто также и вернуть строку 'entry_point'.

        """
        pass

    async def move_next_and_send_message_to_event_loop(self, move_to: str, prev_state: str, message: dict, context: dict, chat: "ChatInterface"):
        self.send_message_to_event_loop(message, context, chat)
        new_state = self.move_next(context, move_to, prev_state)
        return new_state
    
    async def move_back_and_send_message_to_event_loop(self, message: dict, context: dict, chat: "ChatInterface"):
        self.send_message_to_event_loop(message, context, chat)
        new_state = self.move_back(context)
        return new_state

    def move_next(self, context: dict, move_to: str, prev_state: str):
        move_to_state = self.get_entry_point_state() if move_to == "entry_point" else move_to
        prev = self.get_entry_point_state() if prev_state == "entry_point" else prev_state

        context["user_data"]["state_stack"].append(prev)
        context["user_data"]['state'] = move_to_state
        return move_to_state

    def move_back(self, context: dict):
        prev_state = context["user_data"]["state_stack"].pop()
        context["user_data"]['state'] = prev_state
        return prev_state