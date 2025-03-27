from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def get_response(self, message: str) -> str:
        pass

    def set_system_prompt(self, prompt: str):
        pass