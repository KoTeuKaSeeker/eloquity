from abc import ABC, abstractmethod

class DisconnectBotCallbackInterface(ABC):
    @abstractmethod
    def on_disconnect(self, bot):
        pass