from typing import List
from abc import ABC, abstractmethod
from src.bitrix.bitrix_user import BitrixUser

class UserDatabaseInterface(ABC):
    @abstractmethod
    def add_users(self, users: List[BitrixUser]):
        pass

    @abstractmethod
    def find_user(self, sentence: str, max_distance: int = 0, max_count_true: int = 3) -> BitrixUser:
        pass