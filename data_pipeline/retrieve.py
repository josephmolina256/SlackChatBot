import weaviate
import weaviate.classes as wvc
from sentence_transformers import SentenceTransformer

from typing import List, Dict

from .constants import WEAVIATE_COLLECTION_NAME, K_RETRIEVALS, CERTAINTY_THRESHOLD, HF_MODEL_NAME


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

        return res
