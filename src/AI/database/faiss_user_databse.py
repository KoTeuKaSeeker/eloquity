import faiss
import numpy as np
from typing import List
from src.bitrix.bitrix_user import BitrixUser
from sentence_transformers import SentenceTransformer
from src.AI.database.user_database_interface import UserDatabaseInterface


class FaissUserDatabase(UserDatabaseInterface):
    user_vectors: faiss.IndexFlatL2
    users: List[BitrixUser]
    model: SentenceTransformer

    def __init__(self, model: str = "all-MiniLM-L12-v2", vector_size: int = 384):
        self.user_vectors = faiss.IndexFlatL2(vector_size)
        self.model = SentenceTransformer(model)
        self.users = []

    def add_users(self, users: List[BitrixUser]):
        keys = [f"({user.name} {user.last_name}) ({user.last_name} {user.name}) ({user.name} {user.last_name} {user.second_name}) ({user.last_name} {user.name} {user.second_name}))" for user in users]
        vectors = self.model.encode(keys)
        self.user_vectors.add(vectors)
        self.users += users

    def find_user(self, sentence: str, max_distance: int = 0, max_count_true: int = 3) -> BitrixUser:
        query = self.model.encode([sentence])
        distances, indices = self.user_vectors.search(query, k=5)

        return self.users[int(indices[0][0])]