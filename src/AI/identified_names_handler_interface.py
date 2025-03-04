from abc import ABC, abstractmethod

class IdentifiedNamesHandlerInterface():
    @abstractmethod
    def handle_identified_names(name_dict: dict, meet_nicknames: dict, speaker_to_user: dict):
        pass