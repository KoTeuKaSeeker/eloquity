from typing import List
from src.bitrix.bitrix_user import BitrixUser
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility


class UsersDataBase():
    def __init__(self, users: List[BitrixUser], milvis_host: str, milvis_port: str):
        self.model = SentenceTransformer("all-MiniLM-L12-v2")

        connections.connect(host=milvis_host, port=milvis_port)
        self.init_database(users)
    
    def init_database(self, users: List[BitrixUser]):
        self.users = users

        collections = utility.list_collections()
        for collection_name in collections:
            utility.drop_collection(collection_name)

        id_field = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
        vector_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384) 
        user_id_field = FieldSchema(name="user_id", dtype=DataType.INT32)
        
        self.schema = CollectionSchema(fields=[id_field, vector_field, user_id_field])
        self.collection = Collection(name="users_collection", schema=self.schema)

        keys = [f"({user.name} {user.last_name}) ({user.last_name} {user.name}) ({user.name} {user.last_name} {user.second_name}) ({user.last_name} {user.name} {user.second_name}))" for user in users]
        vectors = self.model.encode(keys).tolist()

        self.collection.insert([vectors, list(range(len(users)))])

        self.collection.create_index(
            field_name="embedding",
            index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 32}}
        )

        self.collection.load()
    
    def find_user(self, sentence: str, max_distance: int = 0, max_count_true: int = 3) -> BitrixUser:
        query_vector = self.model.encode([sentence]).tolist()
        
        search_params = {"metric_type": "L2", "params": {"nprobe": 64}}
        results = self.collection.search(query_vector, "embedding", limit=5, param=search_params)[0]

        if max_distance != 0 and results[0].distance > max_distance:
            return None
        
        count_true = 0
        for result in results:
            count_true = int(result.distance <= max_distance)
        
        if count_true > max_count_true:
            return None

        query_result = self.collection.query(expr=f"id == {results[0].id}", output_fields=["user_id"])
        user_id = query_result[0]["user_id"]

        print(results[0].distance)
        return self.users[user_id]
