import os
from uuid import uuid4
from loguru import logger
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct
load_dotenv()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT")

class QdrantService:
    def __init__(self, url=QDRANT_ENDPOINT, api_key=QDRANT_API_KEY):
        """
        Initialize the Qdrant client.
        """
        self.client = QdrantClient(url=url, api_key=api_key)

    def create_collection(self, collection_name, vector_size, distance="Cosine", force_create=False):
        """
        Create a new collection.
        """
        if not self.client.collection_exists(collection_name) or force_create:
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance)
            )
            logger.info(f"Collection '{collection_name}' created.")
        else: logger.info(f"Collection '{collection_name}' have already existed.")

    def insert_vector(self, collection_name, vector_id, vector, payload=None):
        """
        Insert a vector into the collection.
        """
        point = PointStruct(id=vector_id, vector=vector, payload=payload)
        self.client.upsert(collection_name=collection_name, points=[point])
        logger.info(f"Vector with ID {vector_id} inserted into collection '{collection_name}'.")

    def bulk_vectors(self, collection_name: str, vectors: list, payloads: list = None):
        """
        Insert numerous vector into the collection.
        """
        points = []
        for vector, payload in zip(vectors, payloads):
            vector_id = str(uuid4())
            points.append(PointStruct(id=vector_id, vector=vector, payload=payload))
        self.client.upsert(collection_name=collection_name, points=points)
        logger.info(f"Vector with ID {vector_id} inserted into collection '{collection_name}'.")

    def get_vector(self, collection_name, vector_id):
        """
        Retrieve a vector by ID.
        """
        result = self.client.retrieve(
            collection_name=collection_name,
            ids=[vector_id]
        )
        return result[0] if result else None

    def search_vectors(self, collection_name, query_vector, top_k=5):
        """
        Search for the top_k nearest vectors to the query vector.
        """
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return results

    def delete_vector(self, collection_name, vector_id):
        """
        Delete a vector by ID.
        """
        self.client.delete(
            collection_name=collection_name,
            points_selector={"ids": [vector_id]}
        )
        logger.info(f"Vector with ID {vector_id} deleted from collection '{collection_name}'.")

    def delete_collection(self, collection_name):
        """
        Delete an entire collection.
        """
        self.client.delete_collection(collection_name=collection_name)
        logger.info(f"Collection '{collection_name}' deleted.")


# if __name__ == "__main__":
    # qdrant = QdrantService()
    # data = pd.read_csv("model/clean.csv")
    # cv = CountVectorizer(max_features=5000, stop_words='english')
    # vectors = cv.fit_transform(data["Course Description"])