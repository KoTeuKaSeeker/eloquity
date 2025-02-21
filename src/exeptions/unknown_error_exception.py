class UnknownErrorException(Exception):
    def __init__(self):
        super().__init__("Неизвестная ошибка.")