import uuid
from src.domain.command_state_interface import CommandStateInterface

class CommandState(CommandStateInterface):
    state: str
    
    def __init__(self):
        self.state = str(uuid.uuid4())

    def get_command_activate_key(self) -> str:
        return self.state
