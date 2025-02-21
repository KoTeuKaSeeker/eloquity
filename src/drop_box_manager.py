import os
import uuid
import dropbox
import dropbox.exceptions
import requests
from telegram import Update
from src.exeptions.telegram_exceptions.not_supported_format_exception import NotSupportedFormatException
from src.exeptions.dropbox_exceptions.dropbox_is_empty_exception import DropboxIsEmptyException
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.file_extractors.audio_extractor import AudioExtractor
from src.file_extractors.audio_from_video_extractor import AudioFromVideoExtractor

class DropBoxManager():
    dbx: dropbox.Dropbox
    remote_dropbox_folder: str
    audio_dir: str
    video_dir: str
    refresh_token: str
    app_key: str
    app_secret: str

    def __init__(self, remote_dropbox_folder: str, audio_dir: str, video_dir: str, refresh_token: str, app_key: str, app_secret: str):
        self.remote_dropbox_folder = remote_dropbox_folder
        self.audio_dir = audio_dir
        self.video_dir = video_dir
        self.refresh_token = refresh_token
        self.app_key = app_key
        self.app_secret =  app_secret
        self.dbx = dropbox.Dropbox(oauth2_refresh_token=self.refresh_token, app_key=self.app_key, app_secret=self.app_secret)

    def get_user_folder(self, update: Update) -> str:
        dropbox_user_folder = os.path.join(self.remote_dropbox_folder, f"user_{update.message.from_user.id}")
        return dropbox_user_folder
    
    def open_drop_box_file_request(self, update: Update) -> str:
        self.dbx.check_and_refresh_access_token()
        dbx_request = self.dbx.file_requests_create(
            title="Запрос на загрузку файла",
            destination=self.get_user_folder(update),
            deadline=None,
            open=True)
        
        return dbx_request.url

    def load_last_file(self, update: Update) -> str:
        self.dbx.check_and_refresh_access_token()
        from src.format_handlers_manager import allow_audio_extentions, allow_video_extentions
        response = self.dbx.files_list_folder(self.get_user_folder(update))

        files = [entry for entry in response.entries if isinstance(entry, dropbox.files.FileMetadata)]
        latest_file = max(files, key=lambda f: f.server_modified, default=None)

        extention = os.path.splitext(latest_file.name)[1]
        if extention in allow_audio_extentions:
            save_folder = self.audio_dir
        elif extention in allow_video_extentions:
            save_folder = self.video_dir
        else:
            update.message.reply_text(str(NotSupportedFormatException(extention, allow_audio_extentions, allow_video_extentions)))
            return

        file_path = os.path.join(save_folder, latest_file.name)

        with open(file_path, "wb") as f:
            metadata, res = self.dbx.files_download(latest_file.path_lower)
            f.write(res.content)

        return file_path
    
    def load_user_drop(self, update: Update) -> str:
        self.dbx.check_and_refresh_access_token()
        from src.format_handlers_manager import allow_audio_extentions, allow_video_extentions
        try:
            user_folder = self.get_user_folder(update)
            response = self.dbx.files_get_metadata(user_folder)
            is_error = True
            if isinstance(response, dropbox.files.FolderMetadata):
                folder_contents = self.dbx.files_list_folder(user_folder).entries
                if folder_contents:
                    is_error = False
        except dropbox.exceptions.ApiError as e:
            if isinstance(e.error, dropbox.files.GetMetadataError):
              raise DropboxIsEmptyException()
            
        if is_error:
              raise DropboxIsEmptyException()
        

        file_path = self.load_last_file(update)
        is_audio = os.path.splitext(file_path)[1] in allow_audio_extentions
            
        self.dbx.files_delete_v2(self.get_user_folder(update))

        changed_file_path = str(uuid.uuid4()) + ".wav"

        file_extractor = AudioExtractor() if is_audio else AudioFromVideoExtractor()
        file_extractor.extract_file(file_path, changed_file_path)

        return changed_file_path
