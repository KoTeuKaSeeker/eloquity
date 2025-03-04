from abc import ABC, abstractmethod
from typing import List
from src.bitrix.bitrix_task import BitrixTask

class TaskContainerInterface(ABC):
    @abstractmethod
    def find_tasks(self, responsible_id: int = -1, task_id: int = -1, created_by_id: int = -1) -> List[BitrixTask]:
        pass