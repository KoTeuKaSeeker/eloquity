from typing import Any, List
from abc import ABC, abstractmethod
import asyncio

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
        asyncio.create_task(self.send_message_to_event_loop(message, context, chat))
        new_state = self.move_next(context, move_to, prev_state)
        return new_state
    
    async def move_back_and_send_message_to_event_loop(self, message: dict, context: dict, chat: "ChatInterface"):
        self.send_message_to_event_loop(message, context, chat)
        new_state = self.move_back(context)
        return new_state

    def __init_states(self, context: dict):
        if "state_stack" not in context["chat_data"] or len(context["chat_data"]["state_stack"]) == 0:
            context["chat_data"]["state_stack"] = [self.get_entry_point_state()]
        if "state" not in context["chat_data"]:
            context["chat_data"]["state"] = self.get_entry_point_state()


    def move_next(self, context: dict, move_to: str, prev_state: str = None):
        self.__init_states(context)
        move_to_state = self.get_entry_point_state() if move_to == "entry_point" else move_to
        
        prev = context["chat_data"]["state"]
        if prev_state is not None:
            prev = self.get_entry_point_state() if prev_state == "entry_point" else prev_state

        context["chat_data"]["state_stack"].append(prev)
        context["chat_data"]["state"] = move_to_state
        return move_to_state

    def move_back(self, context: dict, count_steps: int = 1):
        self.__init_states(context)
        queue_len = len(context["chat_data"]["state_stack"])
        context["chat_data"]["state_stack"] = context["chat_data"]["state_stack"][:queue_len - count_steps + 1]
        prev_state = context["chat_data"]["state_stack"].pop()
        context["chat_data"]['state'] = prev_state
        return prev_state
    
    def stay_on_state(self, context: dict):
        self.__init_states(context)
        return context["chat_data"]["state"]
        
