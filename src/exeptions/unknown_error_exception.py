from src.exeptions.bot_exception import BotException

class UnknownErrorException(BotException):
    def __init__(self):
        super().__init__("Неизвестная ошибка.")