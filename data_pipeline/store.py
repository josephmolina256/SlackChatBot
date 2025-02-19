import weaviate
import weaviate.classes as wvc
import traceback
from typing import List, Dict

from .constants import WEAVIATE_COLLECTION_NAME, HF_MODEL_NAME


from sentence_transformers import SentenceTransformer

class Storer:
    def __init__(self):
        self.embedding_model = SentenceTransformer(HF_MODEL_NAME)
        self.weaviate_client = weaviate.connect_to_local()
        assert self.weaviate_client.is_live()

    def store(self, json_data: List[Dict]):
        try:
            wv_objs = list()
            for thread in json_data:
                print(thread)
                head = thread["head"]
                responses = thread["responses"]
                thread_ts = thread["thread_ts"]
                channel_id = thread["channel_id"]
                uuid = thread["uuid"]

                embedding = self.embedding_model.encode(head + "\n\n" + responses).tolist()

                wv_objs.append(wvc.data.DataObject(
                    uuid=uuid,
                    properties={
                        "head": head,
                        "responses": responses,
                        "channel_id": channel_id,
                        "thread_ts" : thread_ts
                    },           
                    vector=embedding
                ))

            questions = self.weaviate_client.collections.get(WEAVIATE_COLLECTION_NAME)
            if questions is None:
                questions = self.weaviate_client.collections.create(
                    WEAVIATE_COLLECTION_NAME,
                    vectorizer_config=wvc.config.Configure.Vectorizer.none(),
                )

            questions.data.insert_many(wv_objs)
            print("Stored successfully!")
        except Exception as e:
            print("An error occurred in Storer.store:")
            traceback.print_exc()  # Prints full traceback
            self.weaviate_client.close()
