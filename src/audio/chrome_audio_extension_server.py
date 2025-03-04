from typing import Dict
from dataclasses import dataclass
from enum import Enum
from flask import Flask, request, jsonify
import threading
import uuid
from flask_cors import CORS
import logging


class RecordingState(Enum):
    NOT_RECORDING = 0
    WANT_TO_START_RECORDING = 1
    RECORDING = 2
    WANT_TO_STOP_RECORDING = 3

@dataclass
class BotRecordingState():
    recording_state: RecordingState = RecordingState.NOT_RECORDING
    save_path: str = None

app = Flask("chrome_audio_extension_server")
CORS(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

bot_recording_states: Dict[int, BotRecordingState] = {}
instance_id_to_bot_id: Dict[str, int] = {}

@app.route('/')
def index():
    return "Привет, Flask-сервер работает! Это сообщение для дебага 😉"

@app.route('/recive_bot_id/<instance_id>', methods=['GET'])
def recive_bot_id(instance_id):
    happened = False
    bot_id = -1

    # if instance_id_int not in instance_id_to_bot_id:
        # error_message = f"Расширение записи пытается получить bot_id, но сервер не может его иденцифицировать, так как не знает intance_id = {instance_id} расширения."
        # logging.error(error_message)
        # raise RuntimeError(error_message)
    
    if instance_id in instance_id_to_bot_id:
        happened = True
        bot_id = instance_id_to_bot_id[instance_id]        
    
    response = {
        "event": {
            "happened": happened,
            "bot_id": bot_id
        }
    }

    return jsonify(response)

@app.route('/start_recording_pooling/<bot_id>', methods=['GET'])
def start_recording_pooling(bot_id):
    bot_id_int = int(bot_id)
    if bot_id_int not in bot_recording_states:
        bot_recording_states[bot_id_int] = BotRecordingState()
    
    state = bot_recording_states[bot_id_int]
    
    happened = state.recording_state == RecordingState.WANT_TO_START_RECORDING
    if happened:
        state.recording_state = RecordingState.RECORDING

    response = {
        "event": {
            "happened": happened,
            "save_path": state.save_path
        }
    }

    return jsonify(response)

@app.route('/stop_recording_pooling/<bot_id>', methods=['GET'])
def stop_recording_pooling(bot_id):
    bot_id_int = int(bot_id)
    if bot_id_int not in bot_recording_states:
        bot_recording_states[bot_id_int] = BotRecordingState()
    
    state = bot_recording_states[bot_id_int]

    happened = state.recording_state == RecordingState.WANT_TO_STOP_RECORDING
    if happened:
        state.recording_state = RecordingState.NOT_RECORDING

    response = {
        "event": {
            "happened": happened
        }
    }

    return jsonify(response)


class ChromeAudioExtensionServer():    
    host: str
    port: int
    bot_recording_states: Dict[int, BotRecordingState]

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.bot_recording_states = bot_recording_states
    
    def run_server(self):
        server_thread = threading.Thread(target=lambda: app.run(host=self.host, port=self.port, debug=False), daemon=True)
        server_thread.start()
        return self
    
    def start_recording(self, bot_id: int):
        if bot_id not in self.bot_recording_states:
            filename = str(uuid.uuid4()) + ".wav"
            self.bot_recording_states[bot_id] = BotRecordingState(save_path=filename)
        
        if self.bot_recording_states[bot_id].recording_state != RecordingState.NOT_RECORDING:
            raise ValueError(f"Вы пытаетесь начать запись, но состояние записи у бота {self.bot_recording_states[bot_id].recording_state}")

        self.bot_recording_states[bot_id].recording_state = RecordingState.WANT_TO_START_RECORDING
    
    def stop_recording(self, bot_id: int):
        if bot_id not in self.bot_recording_states:
            return

        if self.bot_recording_states[bot_id].recording_state != RecordingState.RECORDING:
            raise ValueError(f"Вы пытаетесь остановить запись, но состояние записи у бота {self.bot_recording_states[bot_id].recording_state}")
    
        self.bot_recording_states[bot_id].recording_state = RecordingState.WANT_TO_STOP_RECORDING
    
    def get_bot_recording_state(self, bot_id: int):
        return self.bot_recording_states[bot_id]




    
