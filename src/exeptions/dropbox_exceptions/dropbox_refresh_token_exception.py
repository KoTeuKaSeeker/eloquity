class DropboxRefreshTokenException(RuntimeError):
    def __init__(self, response):
        super().__init__("Ошибка при запросе на получение dropbox acces_token 🔑.", response)
        self.response = response