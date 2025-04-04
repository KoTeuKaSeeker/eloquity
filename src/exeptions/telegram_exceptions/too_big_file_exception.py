from src.drop_box_manager import DropBoxManager
from telegram import Update

class TooBigFileException(OSError):
    def __init__(self):
        super().__init__("Файл слишком большой. Максимальный размер загружаемых файлов для телеграм ботов составляет 50 Мб. Если вы загружаете диалог в видеоформате, попробуйте использовать аудиоформат - он гораздо более ёмкий.")
    
    def open_dropbox_response(self, context: dict, drop_box_manager: DropBoxManager) -> str:
        url = drop_box_manager.open_drop_box_file_request(context)

        header = "⏮️ Обработка файла не удалась:"
        general = f"Максимальный доступный размер загружаемых файлов для телеграм ботов состаляет 50 Мб. Если вы хотите загрузить файл большего размера, отправьте его по следующей ссылке: {url}"
        text_end = 'После загрузки нажмите кнопку "Загрузить файл из dropbox"'
        message = f"{header}\n{general}\n{text_end}"
        
        return message