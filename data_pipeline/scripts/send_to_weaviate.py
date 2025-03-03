import weaviate
import weaviate.classes as wvc
import json
import uuid as uuidGen

import weaviate.classes as wvc


from sentence_transformers import SentenceTransformer

try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    with open("./data/qa_store.json", "r") as f:
        json_data = json.load(f)

    f.close()

    question_objs = list()
    for qa in json_data:
        question = qa["question"]
        answer = qa["answer"]
        if "uuid" not in qa:
            qa["uuid"] = uuidGen.uuid4().hex
        uuid = qa["uuid"]
        embedding = embedding_model.encode(question + "\n\n" + answer).tolist()
        question_objs.append(wvc.data.DataObject(
            uuid=uuid,
            properties={
                "question": question,
                "answer": answer,
            },           
            vector=embedding
        ))

    client = weaviate.connect_to_local()

    with open("./data/qa_store.json", "w") as f:
        json.dump(json_data, f, indent=4)

    assert client.is_live()  # This will raise an exception if the client is not live

    questions = client.collections.get("slack_questions")
    if questions is None:
        questions = client.collections.create(
            "slack_questions",
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
        )

    questions.data.insert_many(question_objs)
    client.close()

except Exception as e:
    print(e)
    client.close()
