from typing import Dict, Callable, Any, List
from src.commands.command_interface import CommandInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.chat.chat_interface import ChatInterface
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.dropbox_audio_loader import DropboxAudioLoader
from src.chat_api.file_containers.path_file_container import PathFileContainer
from src.drop_box_manager import DropBoxManager

class DropboxCommand(CommandInterface):
    dropbox_audio_loader: DropboxAudioLoader

    def __init__(self, dropbox_manager: DropBoxManager, filters_factory: MessageFilterFactoryInterface):
        self.dropbox_audio_loader = DropboxAudioLoader(dropbox_manager)
        self.filters_factory = filters_factory

    async def from_dropbox_handler(self, message: dict, context: dict, chat: ChatInterface):
        chat_functions_stack = chat.get_chat_functions_stack()

        not_prev_function_error = False
        if context["chat_id"] not in chat_functions_stack:
            not_prev_function_error = True
        elif len(chat_functions_stack[context["chat_id"]]) == 0:
            not_prev_function_error = True
        
        if not_prev_function_error:
            chat.send_message_to_query("👻 Команда /from_dropbox была вызвана сама по себе. Перед командой /from_dropbox должна быть вызвана команда, которая пытается загрузить большой файл, но не может.")


        backup_function, (backup_message, backup_context, backup_context) = chat.get_chat_functions_stack()[context["chat_id"]]

        audio_path = await self.dropbox_audio_loader.load_audio(message, context, chat)
        audio_container = PathFileContainer(audio_path)
        backup_message["audio_container"] = audio_container

        return await backup_function(backup_message, backup_context, backup_context)

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {
            "global_state_before": [
                MessageHandler(self.filters_factory.create_filter("command", dict(command="from_dropbox")), self.from_dropbox_handler)
            ]
        }