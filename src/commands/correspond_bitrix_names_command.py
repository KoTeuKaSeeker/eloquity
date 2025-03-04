import os
import uuid
from typing import List
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from src.commands.command_interface import CommandInterface
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.ai_exceptions.ai_cant_handle_request_exception import AICantHandleRequestException
from src.exeptions.ai_exceptions.gptunnel_required_payment_exception import GptunnelRequiredPaymentException
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.task_extractor import TaskExtractor
from telegram.ext._handlers.basehandler import BaseHandler
from src.AI.identified_names_handler_interface import IdentifiedNamesHandlerInterface
import logging
import json
import requests

WAITING_FOR_CORRECTIONS = range(3)

class CorrespondBitrixNamesCommand(CommandInterface, IdentifiedNamesHandlerInterface):
    def __init__(self, audio_loader: AudioLoaderInterface, task_extractor: TaskExtractor, transcricribe_request_log_dir: str):
        pass
    
    def handle_identified_names(name_dict: dict, meet_nicknames: dict, speaker_to_user: dict):
        pass

    def entry_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return 
    
    

    def get_telegram_handlers(self) -> List[BaseHandler]:
        return [
            ConversationHandler(
                entry_points=[MessageHandler(filters.ALL, self.handle_command)],
                states={
                    WAITING_FOR_CORRECTIONS: [
                        MessageHandler(filters.Text, self.waiting_for_meet_handling_message),
                    ],
                    WAITING_UNTILL_HANDLING: [
                        CommandHandler("waiting_untill_handling_continue", self.meet_handling_complete_callback),
                        CommandHandler("stop_recording", self.stop_recording),
                        MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.waiting_for_meet_handling_message),
                    ],
                    WAITING_FOR_AUDIO: [
                        MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.conversation_not_ended_message)
                    ]
                },
                fallbacks=[CommandHandler("cancel", self.cancel)])
        ]