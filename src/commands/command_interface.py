from abc import ABC, abstractmethod
from typing import List, Dict
from src.chat_api.message_handler import MessageHandler
from src.chat_api.message_handler import MessageHandler

class CommandInterface(ABC):
    """
        Особые состояния:
        1. entry_point - состояние, которое включается самым первым при запуске бота
        2. global_state_before - не особо даже состояние. Скорее, все хендлеры, которые будут сюда заноситься будут работать всегда, причём будут
        проверяться ДО любых хендлеров из обычных состояний
        3. global_state_after - тоже самое, что и состояние под номером 2, но все хендлеры будут проверяться ПОСЛЕ любых хендлеров из обычных состояний
    """

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {}