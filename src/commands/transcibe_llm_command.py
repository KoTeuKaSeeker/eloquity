from typing import Dict
from src.commands.llm_command import LLMCommand
from src.AI.llm.llm_interface import LLMInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.chat.chat_interface import ChatInterface
from src.transcribers.transcriber_interface import TranscriberInterface
from src.chat_api.file_containers.file_container_interface import FileContainerInterface
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.dropbox_audio_loader import DropboxAudioLoader
from src.chat_api.file_containers.path_file_container import PathFileContainer
from typing import List
import os
import uuid

class TranscibeLLMCommand(LLMCommand):
    transcriber: TranscriberInterface
    temp_path: str

    def __init__(self, model: LLMInterface, filter_factory: MessageFilterFactoryInterface, transcriber: TranscriberInterface, temp_path: str,  entry_point_state: str, dropbox_manager: DropBoxManager):
        super().__init__(model, filter_factory)
        self.dropbox_loader = DropboxAudioLoader(dropbox_manager)
        self.transcriber = transcriber
        self.temp_path = temp_path
        self.transcribe_state = entry_point_state
        self.chatting_state = "transcribe_llm_command.chatting_state"
        self.active_keyboard = None
    
    async def transcirbe_audio(self, message: dict, context: dict, chat: ChatInterface):

        if "messages_history" not in context["chat_data"]:
            context["chat_data"]["messages_history"] = [{"role": "system", "content": self.system_prompt}]
        messages_history: List[dict] = context["chat_data"]["messages_history"]

        audio_container: FileContainerInterface = message["audio_container"]
        file_path = await audio_container.get_file_path()

        transcribe_result = self.transcriber.transcript_audio(file_path)
        transcription = "\n".join(f"speaker_{segment.speaker_id}: {segment.text}" for segment in transcribe_result.segments)

#         transcription = """Интервьюер: Добрый день, спасибо, что нашли время для интервью. Давайте начнем с того, чтобы вы рассказали немного о своем опыте в области машинного обучения.

# Кандидат: Добрый день, спасибо за возможность. Я работаю в области машинного обучения более 8 лет. Начинал с анализа данных, использовал Python и библиотеки вроде Pandas и Scikit-learn для предсказаний и классификаций. В последние несколько лет я фокусируюсь на нейронных сетях и разработке LLM моделей. Работал с такими технологиями, как TensorFlow и PyTorch, а также с крупными моделями, подобными GPT.

# Интервьюер: Отлично. Можете рассказать подробнее о своем опыте работы с LLM моделями?

# Кандидат: Конечно. Моя основная роль заключалась в оптимизации и обучении моделей для обработки естественного языка. Мы использовали подходы глубокого обучения для создания моделей, которые могли бы отвечать на вопросы, генерировать текст и понимать контекст. Я участвовал в настройке архитектуры модели, а также в разработке алгоритмов для улучшения качества генерации текста и сокращения времени отклика.

# Интервьюер: Это звучит очень интересно. Какие инструменты вы использовали для этого?

# Кандидат: Мы использовали TensorFlow для основной разработки, но для некоторых задач я также применял PyTorch, так как он дает больше гибкости в реализации кастомных слоев. Также я активно работал с CUDA для ускорения вычислений, а для обработки больших данных использовал библиотеки как Dask и Apache Spark. В качестве инструментов для деплоя моделей применяли Kubernetes и Docker.

# Интервьюер: Какие из этих технологий вам наиболее интересны, и в чем вы чувствуете себя наиболее уверенно?

# Кандидат: На данный момент мне особенно интересны крупномасштабные модели, такие как GPT, и я чувствую себя наиболее уверенно в области их оптимизации и масштабирования. Я люблю разбираться в тонкостях архитектуры моделей и улучшать их производительность. Однако также важно понимать, как правильно интегрировать модель в рабочие процессы, поэтому я уделяю много внимания DevOps практикам.

# Интервьюер: Понял. Как вы справляетесь с многозадачностью и управлением проектами в таких крупных командах?

# Кандидат: В моем опыте я часто работал в мультидисциплинарных командах. Для эффективной работы я всегда ставлю четкие приоритеты и использую гибкие методологии разработки, такие как Agile. Важно поддерживать постоянную связь с коллегами, чтобы все шаги были согласованы. Я также уделяю внимание автоматизации процессов, чтобы минимизировать рутинную работу.

# Интервьюер: Звучит, как хороший подход. Что вы думаете о будущих тенденциях в области машинного обучения?

# Кандидат: Я считаю, что LLM и модели на базе трансформеров будут продолжать развиваться, и все больше компаний начнут использовать их для решения конкретных задач. Также вижу большой потенциал в применении таких технологий, как reinforcement learning, для адаптивных систем. В будущем будут важны еще более эффективные алгоритмы и способы оптимизации моделей, чтобы делать их менее затратными с точки зрения вычислений и времени.

# Интервьюер: Спасибо за подробный ответ. Мы продолжим анализировать кандидатов, и я свяжусь с вами после завершения интервью. Спасибо за ваше время.

# Кандидат: Спасибо вам. Было приятно пообщаться."""
        
        transcription_name = str(uuid.uuid4())
        transcription_path = os.path.join(self.temp_path, transcription_name)
        with open(transcription_path, "w", encoding="utf-8") as file:
            file.write(transcription)

        await chat.send_message_to_query("🚀 Транскрибация успешно завершена:")
        await chat.send_file_to_query(transcription_path)

        # context["chat_data"]["model_context"] = transcription

        prompt = f"""
        Пользователь отправил транскрипцию интерьвью. Твоя задача сейчас - запомнить транскрипицию и сказать пользователю, 
        что ему нужно предоставить формат работы с транскрипицией. Например, чтобы пользователь попросил сделать кранкое резюме по транскрипции 
        или проверку соответвия кандидата предоставленному чек листу.

        Вот транскриация:

        {transcription}
        """

        user_message = {"role": "user", "content": prompt}
        

        context["chat_data"]["messages_history"].append(user_message)

        return await self.after_transcribe_message(message, context, chat)
    
    async def after_transcribe_message(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("⏮️ Сейчас можете продолжить беседу с ботом - он имеет транскрибацию в памяти.")
        return chat.move_next(context, self.chatting_state)

    async def waiting_audio_message(self, message: dict, context: dict, chat: ChatInterface):
        message = "⏮️ Отправьте аудиозапись для продолжения взаимодействия с ботом."
        if self.active_keyboard is not None:
            await chat.send_keyboad(message, self.active_keyboard)
        else:
            self.active_keyboard = [["Создать dropbox ссылку"]]
            await chat.send_keyboad(message, self.active_keyboard)
        return chat.stay_on_state(context)
    
    async def create_dropbox_link(self, message: dict, context: dict, chat: ChatInterface):
        dropbox_url = self.dropbox_loader.dropbox_manager.open_drop_box_file_request(context)
        
        self.active_keyboard = [["Загрузить файл из dropbox", "Создать dropbox ссылку"]]
        await chat.send_keyboad(f"✨ Создана ссылка для загрузки файла в dropbox:\n{dropbox_url}", self.active_keyboard)
        
        return chat.stay_on_state(context)

    async def from_dropbox_handler(self, message: dict, context: dict, chat: ChatInterface):
        audio_path = await self.dropbox_loader.load_audio(message, context, chat)
        if audio_path is None:
            return chat.stay_on_state(context)
        file_container = PathFileContainer(audio_path)
        message["audio_container"] = file_container

        await chat.send_message_to_query("🧨 Аудио успешно загружено из dropbox.")

        return await self.transcirbe_audio(message, context, chat)

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        states = super().get_conversation_states()
        
        audio_trancribe_states = [
            MessageHandler(self.filter_factory.create_filter("audio"), self.transcirbe_audio),
            MessageHandler(self.filter_factory.create_filter("voice"), self.transcirbe_audio),
            MessageHandler(self.filter_factory.create_filter("video"), self.transcirbe_audio),
            MessageHandler(self.filter_factory.create_filter("all"), self.waiting_audio_message)
        ]

        dropbox_states = [
                MessageHandler(self.filter_factory.create_filter("equal", dict(messages=["Создать dropbox ссылку", "1"])), self.create_dropbox_link),
                MessageHandler(self.filter_factory.create_filter("equal", dict(messages=["Загрузить файл из dropbox", "2"])), self.from_dropbox_handler)
            ]

        states[self.transcribe_state] = dropbox_states + audio_trancribe_states
        states[self.chatting_state] = dropbox_states + states[self.chatting_state] + audio_trancribe_states

        return states