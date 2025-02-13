from src.exeptions.bot_exception import BotException

class AICantHandleRequestException(BotException):
    def __init__(self, reason):
        self.error_message = f"Модель не смогла распределить задачи. Попробуйте загрузить другую аудиозапись.\n ❄️ Причина:\n{reason}"

