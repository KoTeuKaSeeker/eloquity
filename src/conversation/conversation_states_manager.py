from typing import Dict, List
from telegram.ext import ConversationHandler
from telegram.ext._handlers.basehandler import BaseHandler
from enum import Enum
from telegram.ext import ContextTypes


class ConversationState(Enum):
    waiting = 0
    speaker_correction_state_with_preloaded_names = 1
    path_speaker_correction_state_with_preloaded_names = 2
    message_speaker_correction_state_with_preloaded_names = 3
    message_speaker_correction_state = 4
    dropbox_speaker_correction_state = 5
    google_meet_waiting_for_connection = 6
    google_meet_waiting_untill_handling = 7

def move_next(context: ContextTypes.DEFAULT_TYPE, move_to: ConversationState, prev_state: ConversationState):
    context.user_data["state_stack"].append(prev_state)
    context.user_data['state'] = move_to
    return move_to

def move_back(context: ContextTypes.DEFAULT_TYPE):
    prev_state = context.user_data["state_stack"].pop()
    context.user_data['state'] = prev_state
    return prev_state

class ConversationStatesManager():
    conversation_states: Dict[ConversationState, List[BaseHandler]]

    def __init__(self):
        self.conversation_states = {}
        self.entry_points = []
    
    def get_conversation_states(self) -> Dict[ConversationState, List[BaseHandler]]:
        return self.conversation_states

    def add_entry_point(self, handler: BaseHandler):
        self.entry_points.append(handler)

    def add_entry_points(self, handlers: List[BaseHandler]):
        self.entry_points.extend(handlers)

    def add_conversation_state(self, state_name: ConversationState, handlers: List[BaseHandler]):
        if state_name not in self.conversation_states:
            self.conversation_states[state_name] = []
        self.conversation_states[state_name].extend(handlers)
    
    def add_conversation_states(self, states: Dict[ConversationState, List[BaseHandler]]):
        for state_name, handlers in states.items():
            self.add_conversation_state(state_name, handlers)

    def create_conversation_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=self.entry_points,
            states=self.conversation_states,
            fallbacks=[]
        )
