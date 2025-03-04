from typing import List, Dict
from src.google_meet.google_meet_bot import GoogleMeetBot
from src.google_meet.disconnect_bot_callback_interface import DisconnectBotCallbackInterface
from src.audio.audio_recorders.obs_audio_recorder import ObsAudioRecorder
from src.audio.audio_recorders.chrome_extentsion_audio_recorder import ChromeExtentsionAudioRecorder
from src.google_meet.meet_data import MeetData
from src.audio.chrome_audio_extension_server import ChromeAudioExtensionServer

class GoogleMeetBotsManager(DisconnectBotCallbackInterface):
    bots: List[GoogleMeetBot]
    meets_data: Dict[str, List[MeetData]]
    audio_extension_server: ChromeAudioExtensionServer

    def __init__(self, profile_path: str, obs_audio_recorder: ObsAudioRecorder, bot_profile_indices: List[int] = [], show_browser: bool = False):
        self.meets_data = {}
        profiles_count = GoogleMeetBot.get_profiles_count(profile_path)
        if len(bot_profile_indices) == 0:
            bot_profile_indices = list(range(profiles_count))
        
        if any(id < 0 or id >= profiles_count for id in bot_profile_indices):
            raise ValueError(f"Неверное значение индексов профилей ботов. Индексы должны быть в диапазоне от 0 до количества профилей ({profiles_count}) - 1. Указанные индексы ботов:\n {bot_profile_indices}")
        
        self.bots: List[GoogleMeetBot] = [GoogleMeetBot(profile_path, id, obs_audio_recorder, show_browser) for id in bot_profile_indices]
            
        for bot in self.bots:
            bot.set_disconnect_callback(self)

    def get_free_bot(self) -> GoogleMeetBot | None:
        for bot in self.bots:
            if bot.meet_link is None:
                return bot
        return None

    def find_bot(self, meet_link: str) -> GoogleMeetBot | None:
        for bot in self.bots:
            if bot.meet_link == meet_link:
                return bot
        return None

    def connect_bot(self, google_meet_link: str) -> GoogleMeetBot | None:
        free_bot = self.get_free_bot()
        if free_bot is not None:
            free_bot.connect_to_meet(google_meet_link)
        return free_bot

    def on_disconnect(self, bot: GoogleMeetBot):
        if bot.meet_link not in self.meets_data:
            self.meets_data[bot.meet_link] = []
        self.meets_data[bot.meet_link].append(bot.meet_data)
