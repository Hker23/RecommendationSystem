from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct

class QdrantService:
    def __init__(self, host='localhost', port=6333):
        """
        Initialize the Qdrant client.
        """
        self.client = QdrantClient(host=host, port=port)

    def create_collection(self, collection_name, vector_size, distance="Cosine"):
        """
        Create a new collection.
        """
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance)
        )
        logger.info(f"Collection '{collection_name}' created.")

    def insert_vector(self, collection_name, vector_id, vector, payload=None):
        """
        Insert a vector into the collection.
        """
        point = PointStruct(id=vector_id, vector=vector, payload=payload)
        self.client.upsert(collection_name=collection_name, points=[point])
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
