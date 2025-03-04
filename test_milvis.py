from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import numpy as np
from pymilvus import IndexType
from sentence_transformers import SentenceTransformer


if __name__ == "__main__":
    connections.connect(host='192.168.0.11', port='19530')

    collections = utility.list_collections()

    # Drop each collection
    for collection_name in collections:
        utility.drop_collection(collection_name)
        print(f"Dropped collection: {collection_name}")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    sentences = [
        """
a.garibashvili@zebrains.team/
        """,
        """
ay.belov@zebrains.team/
        """,
        """
a.doroshenko@zebrains.team/doralex85@gmail.com
        """,
        """
p.markin@zebrains.team/
        """,
        """
d.dolgov@zebrains.team/emaillit8@gmail.com
        """,
        """
a.dolgov@zebrains.team/emailgax8@gmail.com
        """,
        """
m.tayasnekh@zebrains.team/
        """
    ]



#         """
# ФИО: Гарибашвили Александра
# Почта: a.garibashvili@zebrains.team/
# Должность: Финансовый аналитик
#         """,
#         """
# ФИО: Белов Александр Юрьевич
# Почта: ay.belov@zebrains.team/
# Должность: Менеджер по продажам
#         """,
#         """
# ФИО: Дорошенко Александр Сергеевич
# Почта: a.doroshenko@zebrains.team/doralex85@gmail.com
# Должность: Программист React
#         """,
#         """
# ФИО: Маркин Павел Юрьевич
# Почта: p.markin@zebrains.team/
# Должность: Программист
#         """,
#         """
# ФИО: Долгов Данил Петрович
# Почта: d.dolgov@zebrains.team/emaillit8@gmail.com
# Должность: ML инженер
#         """,
#         """
# ФИО: Долгов Александр Петрович
# Почта: a.dolgov@zebrains.team/emailgax8@gmail.com
# Должность: ML инженер
#         """,
#         """
# ФИО: Таяснех Мишель Файсалович
# Почта: m.tayasnekh@zebrains.team/
# Должность: Разработчик Bitrix 24
#         """






    # Define the fields in the schema
    id_field = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
    vector_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384) 
    text_field = FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=512)

    # Define the collection schema
    schema = CollectionSchema(fields=[id_field, vector_field, text_field], description="Example collection with vectors and descriptions")

    collection = Collection(name="example_collection", schema=schema)

    vectors = model.encode(sentences).tolist()

    collection.insert([vectors, sentences])

    collection.create_index(
        field_name="embedding",
        index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
    )

    # Load the collection before performing search
    collection.load()


    query_sentence = "Долгов"
    query_vector = model.encode([query_sentence]).tolist()

    # Correcting the search call
    param = {"metric_type": "L2"}  # Correct parameter format
    results = collection.search(query_vector, "embedding", limit=5, param=param)

    for result in results[0]:
        # print(f"ID: {result.id}, Distance: {result.distance}")
        description = collection.query(expr=f"id == {result.id}", output_fields=["description"])

        print(f"distance: {result.distance}    text: '{description[0]['description']}'")
    
    collection.drop()