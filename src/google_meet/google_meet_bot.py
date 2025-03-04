import os
import sys
from typing import List, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.exeptions.google_meet_bot.no_user_profiles_found_exception import NoUserProfilesFoundException
from src.exeptions.google_meet_bot.incorrect_profile_id_exception import IncorrectProfileIdException
from src.google_meet.disconnect_bot_callback_interface import DisconnectBotCallbackInterface
from src.audio.audio_recorders.audio_recorder_interface import AudioRecorderInterface
from src.google_meet.meet_data import MeetData
import time

class GoogleMeetBot():
    driver: webdriver.Chrome
    meet_link: str
    disconnect_callback: DisconnectBotCallbackInterface
    meet_data: MeetData
    audio_recorder: AudioRecorderInterface
    is_recording: bool

    def __init__(self, profile_path: str, profile_id: str, audio_recorder: AudioRecorderInterface, show_browser: bool = False, extension_path: str = None):
        self.meet_link = None
        self.is_connected = False
        self.disconnect_callback = None
        self.meet_data = MeetData()
        self.telegram_user_id = -1
        self.audio_recorder = audio_recorder
        self.is_recording = False

        options = webdriver.ChromeOptions()
        if not show_browser:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"user-data-dir={profile_path}")
        if extension_path is not None:
            options.add_argument(f"--load-extension={extension_path}")

        profiles_count = GoogleMeetBot.get_profiles_count(profile_path)
        if not isinstance(profile_id, int) or profile_id < 0 or profile_id >= profiles_count:
            raise IncorrectProfileIdException(profile_id, profiles_count)
        
        profile_name = "Default" if profile_id == 0 else f"Profile {profile_id}"

        options.add_argument(f"--profile-directory={profile_name}")

        self.driver_options = options
        self.driver = None
    
    def set_telegram_user_id(self, user_id: int):
        self.telegram_user_id = user_id

    @staticmethod
    def get_chrome_user_data_path():
        if sys.platform.startswith("win"):
            base_path = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
            return os.path.join(base_path, "Google", "Chrome", "User Data")
        elif sys.platform.startswith("linux"):
            return os.path.expanduser("~/.config/google-chrome")
        elif sys.platform.startswith("darwin"):  # macOS
            return os.path.expanduser("~/Library/Application Support/Google/Chrome")
        else:
            raise RuntimeError("Неизвестная операционная система")

    @staticmethod
    def get_profiles_count(profile_path: str) -> int:
        count_profiles = 0
        for file_name in os.listdir(profile_path):
            folder_path = os.path.join(profile_path, file_name)
            if os.path.isdir(folder_path):
                if file_name == "Default" or file_name.startswith("Profile"):
                    count_profiles += 1
        
        if count_profiles == 0:
            raise NoUserProfilesFoundException(profile_path)

        return count_profiles

    def set_disconnect_callback(self, disconnect_callback: DisconnectBotCallbackInterface):
        self.disconnect_callback = disconnect_callback


    def connect_to_meet(self, google_meet_link: str, max_page_loading_time: int = 20, max_accept_call_time: int = 300) -> bool:
        try:
            if self.meet_link is None:
                self.driver = webdriver.Chrome(options=self.driver_options)
                self.driver.get(google_meet_link)
                WebDriverWait(self.driver, max_page_loading_time).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(@data-promo-anchor-id, "w5gBed")]'))
                )

                self.set_microphone_state(mute=True)
                self.set_camera_state(turn_on=False)

                button = self.driver.find_element(By.XPATH, '//button[contains(@data-promo-anchor-id, "w5gBed")]')
                button.click()
                WebDriverWait(self.driver, max_accept_call_time).until(
                    EC.presence_of_element_located((By.XPATH, '//button[contains(@jsname, "CQylAd")]'))
                )
                print("Подключение подтверждено.")
                self.meet_link = google_meet_link
                self.meet_data.link = self.meet_link
            return True
        except Exception as e:
            print("Не удалось подтвердить подключение:", e)
            return False

    def get_memeber_names(self, open_members_menu_time: int = 5) -> List[str]:
        if self.driver is None:
            raise ValueError("Бот не подключен к Google Meet")

        members_button = self.driver.find_element(By.XPATH, '//button[contains(@data-promo-anchor-id, "GEUYHe")]')
        members_button.click()

        members_container_xpath = '//div[contains(@role, "list") and contains(@class, "AE8xFb OrqRRb GvcuGe goTdfd")]'

        WebDriverWait(self.driver, open_members_menu_time).until(
            EC.presence_of_element_located((By.XPATH, members_container_xpath))
        )

        memebers_container = self.driver.find_element(By.XPATH, members_container_xpath)
        participant_elements = memebers_container.find_elements(By.XPATH, '//div[contains(@role, "listitem")]')
        participants = [elem.get_attribute("aria-label") for elem in participant_elements]
        self.meet_data.members = participants
        return participants

    def set_microphone_state(self, mute: bool, wait_time: int = 1):
        if self.driver is None:
            raise ValueError("Бот не подключен к Google Meet")
        
        microphone_xpath = '//div[contains(@data-promo-anchor-id, "aSBQL")]'

        WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, microphone_xpath))
        )

        microphone_button = self.driver.find_element(By.XPATH, microphone_xpath)
        is_muted = microphone_button.get_attribute("data-is-muted") == "true"
        if (mute and not is_muted) or (not mute and is_muted):
            microphone_button.click()


    def set_camera_state(self, turn_on: bool, wait_time: int = 1):
        if self.driver is None:
            raise ValueError("Бот не подключен к Google Meet")
        
        camera_xpath = '//div[contains(@data-promo-anchor-id, "yhZxwc")]'

        WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, camera_xpath))
        )

        camera_button = self.driver.find_element(By.XPATH, camera_xpath)
        camera_turn_on = camera_button.get_attribute("data-is-muted") == "false"
        if (not camera_turn_on and turn_on) or (camera_turn_on and not turn_on):
            camera_button.click()
        
        camera_new_state = camera_button.get_attribute("data-is-muted") == "false"
        if camera_new_state == camera_turn_on:
            camera_blocked_turn_off_xpath = '//button[contains(@jsname, "jkTUXc")]'

            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, camera_blocked_turn_off_xpath))
            )

            camera_blocked_turn_off_button = self.driver.find_element(By.XPATH, camera_blocked_turn_off_xpath)
            camera_blocked_turn_off_button.click()



    def record_while_on_meet(self, audio_save_path: str):
        if self.driver is None:
            raise ValueError("Бот не подключен к Google Meet")
        
        self.start_record_audio()
        
        while self.is_recording:
            try:
                meet_button = self.driver.find_element(By.XPATH, '//button[contains(@jsname, "CQylAd")]')
            except Exception as e:
                break
            if meet_button is None:
                break

            time.sleep(1)
        
        audio_path = self.stop_record_audio(audio_save_path)
        return audio_path

    def start_record_audio(self):
        self.audio_recorder.start_record_audio()
        self.is_recording = True
    
    def stop_record_audio(self, audio_save_path: str):
        audio_path = self.audio_recorder.stop_record_audio(audio_save_path)
        self.is_recording = False
        return audio_path


    def disconnect(self):
        self.disconnect_callback.on_disconnect(self)
        if self.driver is not None:
            self.driver.quit()
        self.driver = None
        
        self.meet_link = None
        self.telegram_user_id = -1
        self.meet_data = MeetData()