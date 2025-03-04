from dataclasses import dataclass

@dataclass
class BitrixTask():
    id: int = -1
    title: str = ""
    created_by_id: int = -1
    responsible_id: int = -1
    status: int = 1
    priority: int = 1
    discription: str = ""
    deadline: str = ""
