from src.domain.navigation_data_interface import NavigationDataInterface
from src.domain.conversation_state_interface import ConversationStateInterface
from src.domain.command_state_interface import CommandStateInterface

class NavigationData(NavigationDataInterface):
    conversation_state: ConversationStateInterface
    command_state: CommandStateInterface

    def __init__(self, conversation_state: ConversationStateInterface = None, command_state: CommandStateInterface = None):
        self.conversation_state = conversation_state
        self.command_state = command_state

    def get_next_state(self) -> ConversationStateInterface | None:
        return self.conversation_state

    def get_next_command_state(self) -> CommandStateInterface | None:
        return self.command_state