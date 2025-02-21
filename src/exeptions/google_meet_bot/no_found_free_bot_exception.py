class NoFoundFreeBotException(RuntimeError):
    def __init__(self):
        super().__init__("Не найдено свободных ботов для подключения к Google Meet. Повторите попытку позже или обработайте запись без подключения к Google Meet.")