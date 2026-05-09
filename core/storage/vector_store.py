import chromadb
from chromadb.utils import embedding_functions

class VectorMemory:
    def __init__(self, collection_name="security_state"):
        self.client = chromadb.PersistentClient(path="./data/vector_db")
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def store_endpoint(self, url, metadata):
        self.collection.add(
            documents=[url],
            metadatas=[metadata],
            ids=[str(hash(url))]
        )

    def query(self, query_text):
        return self.collection.query(query_texts=[query_text], n_results=5)
