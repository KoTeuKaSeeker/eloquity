from typing import List
from dataclasses import dataclass

class MeetData():
    link: str = ""
    members: List[str] = []

    def __init__(self, link: str = "", members: List[str] = []):
        self.link = link
        self.members = members
