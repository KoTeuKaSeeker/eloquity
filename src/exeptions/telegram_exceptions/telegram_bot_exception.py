class TelegramBotException(Exception):

    def __init__(self, exception: Exception):
        super().__init__(exception)
        self.exception = exception

    def __str__(self):
        return f"❌ Ошибка:\n{self.exception.args[0]}"

