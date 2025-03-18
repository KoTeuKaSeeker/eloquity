from abc import ABC, abstractmethod

class FileContainerInterface(ABC):
    @abstractmethod
    async def get_file_path(self):
        pass