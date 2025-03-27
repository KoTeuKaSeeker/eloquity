import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("speechbrain.utils.quirks").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

import colorlog

from typing import Dict, Type, List
import os
from huggingface_hub import login
import torch
from dotenv import load_dotenv
from dependency_injector import containers, providers
from src.transcribers.deepgram_transcriber import DeepgramTranscriber
from src.exeptions.unknown_error_exception import UnknownErrorException
from src.AI.eloquity_ai import EloquityAI
from src.drop_box_manager import DropBoxManager
from src.commands.command_interface import CommandInterface
from src.commands.message_transcribe_audio_command import MessageTranscribeAudioCommand
from src.commands.dropbox_transcribe_audio_command import DropboxTranscribeAudioCommand
from src.commands.start_command import StartCommand
from src.commands.cancel_command import CancelCommand
from src.commands.help_command import HelpCommand
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.google_meet.google_meet_bots_manager import GoogleMeetBotsManager
from src.google_meet.google_meet_bot import GoogleMeetBot
from src.task_extractor import TaskExtractor
from src.audio.audio_recorders.obs_audio_recorder import ObsAudioRecorder
from src.audio.chrome_audio_extension_server import ChromeAudioExtensionServer
from src.bitrix.bitrix_manager import BitrixManager
from src.AI.database.faiss_user_databse import FaissUserDatabase
from src.conversation.conversation_states_manager import ConversationStatesManager
from src.commands.remind_command import RemindCommand
from src.commands.message_transcribe_audio_with_preloaded_names_command import MessageTranscribeAudioWithPreloadedNamesCommand
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.message_filters.factories.base_message_filter_factory import BaseMessageFilterFactory
from src.commands.google_meet_connect_commands.google_meet_connect_command import GoogleMeetConnectCommand
from src.commands.google_meet_connect_commands.google_meet_recording_audio_command import GoogleMeetRecordingAudioCommand
from src.format_corrector import FormatCorrector
from src.commands.transcibe_llm_command import TranscibeLLMCommand
from src.AI.llm.gpttunnel_model import GptunnelModel
from src.AI.llm.llm_interface import LLMInterface
from src.transcribers.transcriber_interface import TranscriberInterface
from src.transcribers.deepgram_transcriber import DeepgramTranscriber

from src.chat_api.chat_api.telegram_chat_api import TelegramChatApi
from src.chat_api.chat_api.openwebui_chat_api import OpenwebuiChatApi
from src.commands.summury_llm_command import SummuryLLMCommand
from src.commands.hr_llm_command import HrLLMCommand
from src.commands.direct_start_command import DirectStartCommand

#TODO #TODO #TODO #TODO #TODO #TODO #TODO #TODO #TODO #TODO
# Транскрибатор падает, если получает на вход запись, в котором не сказанно ни одного слова. 
# Надо исправить эту ошибку - возможно она затрагивает большее количество ситуаций, чем просто "пустая запись".
#TODO #TODO #TODO #TODO #TODO #TODO #TODO #TODO #TODO #TODO


BOT_USERNAME = "zebrains_trascriber_bot"
AUDIO_DIR = "tmp/"
VIDEO_DIR = "tmp/"
DOCX_DIR = "tmp/"
DROPBOX_DIR = "/transcribe_requests/"
DOCX_TEMPLATE_PATH = "docx_templates/default.docx"
LOG_DIR = "logs/"
TRANSCRIBE_REQUEST_LOG_DIR = os.path.join(LOG_DIR, "transcribe_requests")
GOOGLE_CHROME_USER_DATA = GoogleMeetBot.get_chrome_user_data_path()
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "jXy9RT0qcKs93U83"
OBS_RECORDING_DIRECTORY = "C:/Users/Email.LIT/Videos/"
AUDIO_EXTENSION_PATH = "chrome_recorder_extension/"
INSTANCE_ID_SCRIPT_PATH = "js_code/get_instance_id_script.js"
MILVIS_HOST = "localhost"
MILVIS_PORT = "19530"
OPEN_WEB_UI_HOST = "localhost"
OPEN_WEB_UI_PORT = "8001"
SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".m4a"]
SUPPORTED_VIDEO_FORMATS = [".mp4", ".mov"]

def init_logger():
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"

    console_handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
    "%(log_color)s" + LOG_FORMAT,
    datefmt=LOG_DATEFMT,
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
        })
    
    console_handler.setFormatter(formatter)

    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))


    logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        console_handler,
        file_handler
    ],

    force=True
    )

    logging.getLogger("sieve._openapi").setLevel(logging.CRITICAL)
    logging.getLogger("sieve").setLevel(logging.CRITICAL)

def load_commands(
        llm_model: LLMInterface, 
        filter_factory: MessageFilterFactoryInterface, 
        transcriber: TranscriberInterface) -> List[CommandInterface]:
    commands = []

    commands.append(DirectStartCommand(filter_factory, {"summury_assistant": "summury_llm_command", "hr_assistant": "hr_llm_command"}))
    commands.append(SummuryLLMCommand(llm_model, filter_factory, transcriber, AUDIO_DIR, entry_point_state="summury_llm_command"))
    commands.append(HrLLMCommand(llm_model, filter_factory, transcriber, AUDIO_DIR, entry_point_state="hr_llm_command"))

    return commands

class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    device = providers.Singleton(lambda: "cuda" if torch.cuda.is_available() else "cpu")

    audio_transcriber = providers.Singleton(
        DeepgramTranscriber,
        api_key=config.deepgram_api_key,
    )

    # chat_api = providers.Singleton(
    #     TelegramChatApi,
    #     token=config.telegram_bot_token, 
    #     audio_dir=providers.Object(AUDIO_DIR), 
    #     video_dir=providers.Object(VIDEO_DIR), 
    #     audio_extenstion=providers.Object(".wav")
    # )

    chat_api = providers.Singleton(
        OpenwebuiChatApi,
        openwebui_coordinator_url=providers.Object(f"http://{OPEN_WEB_UI_HOST}:{OPEN_WEB_UI_PORT}/"),
        temp_path=providers.Object(AUDIO_DIR)
    )

    bitrix_manager = providers.Singleton(
        BitrixManager,
        webhook_url=config.bitrix_webhook_url,
    )

    users_database = providers.Singleton(FaissUserDatabase)

    eloquity = providers.Singleton(
        EloquityAI,
        api_key=config.gptunnel_api_key,
        bitrix_manager=bitrix_manager,
        users_database=users_database,
        model_name=providers.Object("gpt-4o-mini"),
    )

    drop_box_manager = providers.Singleton(
        DropBoxManager,
        remote_dropbox_folder=providers.Object(DROPBOX_DIR),
        audio_dir=providers.Object(AUDIO_DIR),
        video_dir=providers.Object(VIDEO_DIR),
        refresh_token=config.dropbox_refresh_token,
        app_key=config.dropbox_app_key,
        app_secret=config.dropbox_app_secret,
    )

    audio_recorder = providers.Singleton(
        ObsAudioRecorder,
        host=config.obs_host,
        port=config.obs_port,
        password=config.obs_password,
        recording_directory=providers.Object(OBS_RECORDING_DIRECTORY),
    )

    google_meet_bots_manager = providers.Singleton(
        GoogleMeetBotsManager,
        profile_path=providers.Object(GOOGLE_CHROME_USER_DATA),
        obs_audio_recorder=audio_recorder,
        bot_profile_indices=providers.Object([1]),
        show_browser=providers.Object(True),
    )

    task_extractor = providers.Singleton(
        TaskExtractor,
        audio_transcriber=audio_transcriber,
        eloquity=eloquity,
        docx_template_path=providers.Object(DOCX_TEMPLATE_PATH),
    )

    conversation_states_manager = providers.Singleton(ConversationStatesManager)

    filter_factory = providers.Singleton(BaseMessageFilterFactory)

    format_corrector = providers.Singleton(
        FormatCorrector,
        supported_audio_formats=providers.Object(SUPPORTED_AUDIO_FORMATS), 
        supported_video_formats=providers.Object(SUPPORTED_VIDEO_FORMATS)
    )
    
    llm_model = providers.Singleton(
        GptunnelModel,
        api_key=config.gptunnel_api_key, 
        model_name=providers.Object("gpt-4o")
    )

    commands = providers.Singleton(
        load_commands,
        llm_model=llm_model,
        filter_factory=filter_factory,
        transcriber=audio_transcriber
    )

def init_container() -> ApplicationContainer:
    """Инициализирует DI-контейнер, загружая конфигурацию из .env и переменных окружения."""
    load_dotenv()  # Загрузка переменных окружения из .env

    container = ApplicationContainer()

    container.config.from_dict({
        'gptunnel_api_key': os.getenv("GPTUNNEL_API_KEY"),
        'telegram_bot_token': os.getenv("TELEGRAM_BOT_TOKEN"),
        'hugging_face_token': os.getenv("HUGGING_FACE_TOKEN"),  # Если понадобится
        'dropbox_app_key': os.getenv("DROPBOX_APP_KEY"),
        'dropbox_app_secret': os.getenv("DROPBOX_APP_SECRET"),
        'dropbox_refresh_token': os.getenv("DROPBOX_REFRESH_TOKEN"),
        'deepgram_api_key': os.getenv("DEEPGRAM_API_KEY"),
        'bitrix_webhook_url': os.getenv("BITRIX_WEBHOOK_URL"),
        'obs_host': os.getenv("OBS_HOST", OBS_HOST),
        'obs_port': int(os.getenv("OBS_PORT", OBS_PORT)),
        'obs_password': os.getenv("OBS_PASSWORD", OBS_PASSWORD),
    })

    return container

if __name__ == "__main__":
    init_logger()

    container = init_container()
    logging.info("Initialization complete. Bot is ready to work")

    conversation_states_manager = container.conversation_states_manager()
    for command in container.commands():
        conversation_states_manager.add_conversation_states(command.get_conversation_states())
        conversation_states_manager.add_entry_points(command.get_entry_points())

    states = conversation_states_manager.create_conversation_states()

    chat_api = container.chat_api()
    chat_api.set_handler_states(states)

    logging.info("Polling for new events")
    chat_api.start(poll_interval=0.5)