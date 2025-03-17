from typing import Dict, List
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface

class ConversationStatesManager():
    conversation_states: Dict[str, List[MessageHandlerInterface]]

    def __init__(self):
        self.conversation_states = {}
        self.entry_points = []

    def add_entry_point(self, handler: MessageHandlerInterface):
        self.entry_points.append(handler)

    def add_entry_points(self, handlers: List[MessageHandlerInterface]):
        self.entry_points.extend(handlers)

    def add_conversation_state(self, state_name: str, handlers: List[MessageHandlerInterface]):
        if state_name == "entry_point":
            self.add_entry_points(handlers)
            return

        if state_name not in self.conversation_states:
            self.conversation_states[state_name] = []
        self.conversation_states[state_name].extend(handlers)
    
    def add_conversation_states(self, states: Dict[str, List[MessageHandlerInterface]]):
        for state_name, handlers in states.items():
            self.add_conversation_state(state_name, handlers)
    
    def create_conversation_states(self) -> Dict[str, List[MessageHandlerInterface]]:
        states = {}
        states.update(self.conversation_states)
        states["entry_point"] = self.entry_points
        return states
