from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request

import os
from dotenv import load_dotenv

from .chatbot.chatbot import HuggingChatWrapper

load_dotenv()

chat_wrapper = HuggingChatWrapper()  # Singleton chat wrapper
chatbot = chat_wrapper.get_chatbot()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SIGNING_SECRET"))

def get_channel_id(channel_name: str):
    response = app.client.conversations_list()
    # print(json.dumps(response["channels"], indent=4))
    for channel in response["channels"]:
        if channel["name"] == channel_name:
            return channel["id"]
    return None
BOT_PRACTICE_CHANNEL_ID = get_channel_id("random")
print(BOT_PRACTICE_CHANNEL_ID)


import json
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_qa_data(file_path="./data/qa_store.json"):
    with open(file_path, "r") as file:
        return json.load(file)
    
qa_data = load_qa_data()
qa_embeddings = {item["question"]: embedding_model.encode(item["question"]) for item in qa_data}


def retrieve_similar_question(user_query, threshold=0.3):
    """Finds the most similar question from the stored Q&A pairs and returns both the question and answer."""
    user_embedding = embedding_model.encode(user_query)

    best_match = None
    best_score = float("inf")

    for question, embedding in qa_embeddings.items():
        score = cosine(user_embedding, embedding)
        if score < best_score:  # Lower cosine distance = higher similarity
            best_score = score
            best_match = question

    # Return both question and answer if similarity is above threshold
    if best_score < threshold:
        for item in qa_data:
            if item["question"] == best_match:
                return {"question": best_match, "answer": item["answer"]}
    
    return None



@app.event("message")
def handle_message(event, say):
    print("received event!")
    if event.get("channel_type") == "im":
        user_message = event.get("text")
        user_id = event.get("user")
        res = ""

        if user_message and isinstance(user_message, str):
            if user_message.startswith("Echo:"):
                res = f"Hey <@{user_id}>, you said: {user_message[5:]}"
            elif user_message.startswith("Chat:"):
                print("Generating a response...")

                # Retrieve similar Q&A pair
                retrieved_qa  = retrieve_similar_question(user_message)

                # Build context for the LLM
                context = (
                    f"User asked: {user_message}\n"
                    "Here is a related Q&A pair that may help answer the question:\n"
                    f"Q: {retrieved_qa['question']}\n"
                    f"A: {retrieved_qa['answer']}\n"
                    "Now generate the best response based on this information.\n\n"
                )

                # Pass the context-enhanced message to the chatbot
                res = context + chat_wrapper.get_chatbot().chat(context).wait_until_done()
            else:
                res = ('Please use one of the following prefixes:\n'
                      '"Echo:",\n' 
                      '"Chat:"')

        say(res)


@app.event("app_mention")
def handle_bot_practice_channel_messages(event, say):
    """Handles messages where the bot is mentioned in the 'random' channel and replies in a thread."""
    if event.get("channel") == BOT_PRACTICE_CHANNEL_ID:  
        user_message = event.get("text")
        user_id = event.get("user")

        # Use 'thread_ts' if it's provided, otherwise, reply in a new thread
        thread_ts = event.get("thread_ts") or event.get("ts")  

        say(
            text=f"Hello <@{user_id}>, you said in #random: {user_message}",
            thread_ts=thread_ts  # Reply in the same thread
        )


fastapi_app = FastAPI()

handler = SlackRequestHandler(app)

@fastapi_app.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)

@fastapi_app.get("/")
def ping():
    return {"response": "Hello World"}


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=3000)
