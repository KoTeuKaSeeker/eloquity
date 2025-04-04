class DropboxIsEmptyException(RuntimeError):
    def __init__(self):
        super().__init__("В dropbox не был загружен файл.")
    
    def open_dropbox_request(self, context: dict, drop_box_manager) -> str:
        url = drop_box_manager.open_drop_box_file_request(context)
        str1 = f"⏮️ В dropbox не был загружен файл. Загрузите файл по следующей ссылке: {url}"
        str2 = 'После загрузки нажмите кнопку "Загрузить файл из dropbox"'
        return f"{str1}\n{str2}"