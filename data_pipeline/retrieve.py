import weaviate
import weaviate.classes as wvc
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer

import atexit
from typing import List, Dict

from .constants import WEAVIATE_COLLECTION_NAME, K_RETRIEVALS, CERTAINTY_THRESHOLD, HF_MODEL_NAME


app = FastAPI()

class Retriever:
    def __init__(self):
        self.weaviate_client = weaviate.connect_to_local()
        assert self.weaviate_client.is_live()
        self.embedding_model = SentenceTransformer(HF_MODEL_NAME)

    def retrieve(self, question: str) -> List[Dict]:
        questions = self.weaviate_client.collections.get(WEAVIATE_COLLECTION_NAME)
        query_vector = self.embedding_model.encode(question).tolist()

        response = questions.query.near_vector(
            near_vector=query_vector,
            limit=K_RETRIEVALS,
            return_metadata=wvc.query.MetadataQuery(certainty=True),
            certainty=CERTAINTY_THRESHOLD,
        )

        res = []
        for object in response.objects:
            res.append(
                {
                    "certainty": object.metadata.certainty,
                    "properties": object.properties
                }
            )
            print(object.metadata.certainty)
            print(object.properties)
            print("\n\n")
        return res

retriever = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/spawn_retriever")
def spawn_retriever():
    global retriever
    retriever = Retriever()
    return {"message": "Retriever spawned"}

@app.get("/retrieve")
def retrieve(question: str):
    response = retriever.retrieve(question)
    return response


def close_client():
    if retriever and retriever.weaviate_client:
        retriever.weaviate_client.close()

atexit.register(close_client)