from typing import Dict, List, Callable, Any
from src.outer_domain.command_handler_interface import CommandHandlerInterface
from src.domain.conversation_state_interface import ConversationStateInterface
from src.domain.conversation_manager_interface import ConversationManagerInterface
from src.outer_domain.command_handler_connector_interface import CommandHandlerConnectorInterface

class ConversationManager(ConversationManagerInterface):
    states: Dict[ConversationStateInterface, List[CommandHandlerInterface]]
    command_handler_connector: CommandHandlerConnectorInterface

    def __init__(self, command_handler_connector: CommandHandlerConnectorInterface):
        self.states = {}
        self.command_handler_connector = command_handler_connector

    def get_conversation_states(self) -> Dict[ConversationStateInterface, List[CommandHandlerInterface]]:
        return self.states

    def add_states(self, states: Dict[ConversationStateInterface, List[CommandHandlerInterface | List[CommandHandlerInterface]]]):
        for state, command_handlers in states.items():
            command_handlers_list = []
            for command_handler in command_handlers:
                if isinstance(command_handler, list):
                    command_handlers_list.extend(command_handler)
                else:
                    command_handlers_list.append(command_handler)
            self.states[state] = command_handlers_list

    def get_state(self, state: ConversationStateInterface) -> List[CommandHandlerInterface]:
        return self.states[state]

    def get_handler_functions(self) -> Dict[str, Callable[..., Any]]:
        handler_functions = {}
        for state, command_handler in self.states.items():
            handler_functions[state.get_state()] = self.command_handler_connector.get_handler_function(command_handler)
        return handler_functions