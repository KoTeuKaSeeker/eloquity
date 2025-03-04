from src.audio.audio_recorders.audio_recorder_interface import AudioRecorderInterface
from src.audio.chrome_audio_extension_server import ChromeAudioExtensionServer, instance_id_to_bot_id
from src.google_meet.google_meet_bot import GoogleMeetBot
from src.audio.chrome_audio_extension_server import BotRecordingState
from platformdirs import user_downloads_dir
import shutil
import time
import os

class ChromeExtentsionAudioRecorder(AudioRecorderInterface):

    audio_extension_server: ChromeAudioExtensionServer
    bot_id: int
    bot: GoogleMeetBot
    instance_id_script: str

    def __init__(self, audio_extension_server: ChromeAudioExtensionServer, bot_id: str, instance_id_script: str):
        self.audio_extension_server = audio_extension_server
        self.bot_id = bot_id
        self.bot = None
        self.instance_id_script = instance_id_script

    def set_bot(self, bot: GoogleMeetBot):
        self.bot = bot

    def init_connection_to_extention(self):
        if not self.bot_id in instance_id_to_bot_id:
            intsance_id = self.bot.driver.execute_script(self.instance_id_script)
            instance_id_to_bot_id[intsance_id] = self.bot_id


    def start_record_audio(self) -> str:
        self.init_connection_to_extention()
        self.audio_extension_server.start_recording(self.bot_id)
    
    def stop_record_audio(self, save_audio_path: str, time_out: int = 30) -> str:
        self.audio_extension_server.stop_recording(self.bot_id)
        
        bot_recording_state: BotRecordingState = self.audio_extension_server.get_bot_recording_state(self.bot_id)
        
        downloads_dir = user_downloads_dir()
        audio_file_path = os.path.join(downloads_dir, bot_recording_state.save_path)
        start_waiting_time = time.time()
        while True:
            if os.path.exists(audio_file_path):
                break

            if time.time() - start_waiting_time > time_out:
                raise TimeoutError("Превышено время ожидания получения файла записи.")

            time.sleep(1)
        
        shutil.move(audio_file_path, save_audio_path)

        return save_audio_path