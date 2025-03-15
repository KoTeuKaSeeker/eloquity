class DropboxIsEmptyException(RuntimeError):
    def __init__(self):
        super().__init__("В dropbox не был загружен файл.")
    
    def open_dropbox_request(self, context: dict, drop_box_manager) -> str:
        url = drop_box_manager.open_drop_box_file_request(update)
        str1 = f"⏮️ В dropbox не был загружен файл. Загрузите файл по следующей ссылке: {url}"
        str2 = f"После загрузки файла повторите команду /from_dropbox"
        return f"{str1}\n{str2}"