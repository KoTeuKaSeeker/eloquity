import uuid
from src.domain.conversation_state_interface import ConversationStateInterface

class ConversationState(ConversationStateInterface):
    state: str
    
    def __init__(self):
        self.state = str(uuid.uuid4())

    def get_state(self) -> str:
        return self.state

