class BotException(Exception):
    error_message: str

    def __init__(self, error_message: str = ""):
        self.error_message = error_message

    def __str__(self):
        return f"❌ Ошибка:\n{self.error_message}"

