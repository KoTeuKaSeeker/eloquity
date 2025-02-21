from typing import Callable
import sounddevice as sd
import numpy as np
import wave
import time
import os

class AudioRecorder():
    channels: int
    sample_rate: int

    def __init__(self, channels: int = 1, sample_rate: int = 16000):
        self.channels = channels
        self.sample_rate = sample_rate
    
    async def record(self, device_name: str, save_path: str, record_untill_callback: Callable[[], bool], max_duration: int = 36000) -> str:
        if os.path.splitext(save_path)[1] != ".wav":
            raise ValueError("Сохраняемый аудиофайл должен имет расширение '.wav'")

        devices = sd.query_devices()
        loopback_device_id = -1

        for i, device in enumerate(devices):
            if device_name.lower() in device["name"].lower():
                loopback_device_id = i
                break
        
        if loopback_device_id < 0:
            raise ProcessLookupError(f"При попытке считывания аудиопотока, не удалось найти устройство с названием '{device_name}'. Список доступных устройств:\n {devices}")
        
        audio_data = np.zeros((max_duration * self.sample_rate, self.channels), dtype=np.int16)
        global data_index
        data_index = 0
        start_recording_time = time.time()

        def recording_callback(indata, frames, _time, status):
            global data_index
            if status:
                raise sd.CallbackAbort(f"Ошибка записи: {status}")
            
            current_time = time.time()
            elapsed_time = current_time - start_recording_time

            if not record_untill_callback() or data_index + frames > len(audio_data):
                data_index += frames
                sd.stop()
                return
            
            audio_data[data_index:data_index + frames] = indata
            data_index += frames

        with sd.InputStream(callback=recording_callback, device=loopback_device_id, channels=self.channels, dtype=np.int16, samplerate=self.sample_rate):
            while data_index < len(audio_data):
                time.sleep(0.1)

        with wave.open(save_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        return save_path