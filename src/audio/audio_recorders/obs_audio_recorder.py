from src.audio.audio_recorders.audio_recorder_interface import AudioRecorderInterface
from obswebsocket import obsws, requests
from src.file_extractors.audio_from_video_extractor import AudioFromVideoExtractor
import os
import glob
import time

class ObsAudioRecorder(AudioRecorderInterface):
    ws: obsws
    scene_name: str
    recording_directory: str

    def __init__(self, host: str, port: int, password: str, recording_directory: str, scene_name: str = "audio_transcriber_scene"):
        self.scene_name = scene_name
        self.ws = obsws(host, port, password)
        self.audio_from_video_extractor = AudioFromVideoExtractor()
        self.recording_directory = recording_directory

    def start_record_audio(self, process_name: str) -> str:
        self.ws.connect()
        scenes_response = self.ws.call(requests.GetSceneList())
        scenes = scenes_response.getScenes()

        if not any(scene["sceneName"] == self.scene_name for scene in scenes):  
            raise Exception(f"Не найденно подготовленной цены для записи звука (должно быть название {self.scene_name}). Создайте и настройте необходимую сцену.")
        
        self.ws.call(requests.SetCurrentProgramScene(sceneName=self.scene_name))
        self.ws.call(requests.StartRecord())
    
    def stop_record_audio(self, save_audio_path: str, process_name: str = "") -> str:
        self.ws.call(requests.StopRecord())
        self.ws.disconnect()
        time.sleep(1)
        
        # Получаем список файлов в директории
        files = glob.glob(os.path.join(self.recording_directory, "*"))
        if not files:
            raise Exception("В директории записи OBS не найдено файлов.")
        
        # Выбираем файл с максимальным временем модификации
        latest_file = max(files, key=os.path.getmtime)
        
        self.audio_from_video_extractor.extract_file(latest_file, save_audio_path, remove_parent=True)
        
        return save_audio_path