from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GoogleMeetBot():
    driver: webdriver.Chrome
    _is_connected: bool = False

    def __init__(self, google_meet_link: str, profile_path: str, show_browser: bool = False):
        options = webdriver.ChromeOptions()
        if show_browser:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"user-data-dir={profile_path}")

        driver = webdriver.Chrome(options=options)
        driver.get(google_meet_link)
        self.driver = driver
    
    def _wait_for_connection(self, timeout=20) -> bool:
        try:
            if not self._is_connected:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".meeting-connected"))
                )
                print("Подключение подтверждено.")
                self._is_connected = True
            return True
        except Exception as e:
            print("Не удалось подтвердить подключение:", e)
            return False

    def get_memeber_names(self, loading_time: int = 5) -> List[str]:
        self._wait_for_connection()
        try:
            participants_container = WebDriverWait(self.driver, loading_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".participants-list"))
            )
            
            # Находим элементы участников внутри контейнера
            participant_elements = participants_container.find_elements(By.CSS_SELECTOR, ".participant-item")
            
            # Собираем текст каждого участника в список
            participants = [elem.text for elem in participant_elements]
            return participants
        except Exception as e:
            print("Ошибка:", e)
            return []

    def disconnect(self):
        # TODO
        self.driver.quit()