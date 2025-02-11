from src.exeptions.bot_exception import BotException

class DropboxRefreshTokenException(BotException):
    def __init__(self, response):
        super().__init__("Ошибка при запросе на получение dropbox acces_token 🔑.")
        self.response = response