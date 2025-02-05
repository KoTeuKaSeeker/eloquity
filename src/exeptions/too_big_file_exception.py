from src.exeptions.bot_exception import BotException
from src.drop_box_manager import DropBoxManager
from telegram import Update

class TooBigFileException(BotException):
    def __init__(self):
        self.error_message = "Файл слишком большой. Максимальный размер загружаемых файлов для телеграм ботов составляет 50 Мб. Если вы загружаете диалог в видеоформате, попробуйте использовать аудиоформат - он гораздо более ёмкий."
    
    def open_dropbox_response(self, update: Update, drop_box_manager: DropBoxManager) -> str:
        url = drop_box_manager.open_drop_box_file_request(update)

        header = "⏮️ Обработка файла не удалась:"
        general = f"Максимальный доступный размер загружаемых файлов для телеграм ботов состаляет 50 Мб. Если вы хотите загрузить файл большего размера, отправьте его по следующей ссылке: {url}"
        text_end = f"После загрузки, выполните команду /from_dropbox, чтобы обработать файл."
        message = f"{header}\n{general}\n{text_end}"
        
        return message