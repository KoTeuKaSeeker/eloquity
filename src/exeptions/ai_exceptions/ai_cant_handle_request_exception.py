class AICantHandleRequestException(RuntimeError):
    def __init__(self, reason: str):
        message = f"Модель не смогла распределить задачи. Попробуйте загрузить другую аудиозапись.\n ❄️ Причина:\n{reason}"
        super().__init__(message)

