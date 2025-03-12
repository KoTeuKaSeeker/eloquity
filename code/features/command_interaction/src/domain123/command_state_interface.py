from abc import ABC, abstractmethod

class CommandStateInterface(ABC):
    @abstractmethod
    def get_command_activate_key(self) -> str:
        pass