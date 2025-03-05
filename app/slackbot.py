from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from time import time, sleep

from .chatbot.chatbot import HuggingChatWrapper
from data_pipeline.retrieve import Retriever

from data_pipeline.constants import SLACK_WORKSPACE_NAME


load_dotenv(override=True)

chat_wrapper = HuggingChatWrapper() # Singleton chat wrapper
chatbot = chat_wrapper.get_chatbot()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SIGNING_SECRET"))


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
                print("Generating a response to", user_message)

                retrieved_data = retriever.retrieve(user_message)

                # Build context for the LLM
                if len(retrieved_data) > 0:
                    context = (
                        f"User asked: {user_message[5:]}\n\n"
                        "Here is some information that might be relevant to the question:\n\n"
                    )

                    for i, item in enumerate(retrieved_data):
                        context += f"Q{i+1}:\n{item['properties']['head']}\nA{i+1}:\n{item['properties']['responses']}\n(Relevance Score: {item['certainty']:.2f})\n\n"

                    context += "Now generate the best response based on this information.\n\n"

                    print(context)
                    say(context)
                else:
                    context = (
                        f"User asked: {user_message}\n"
                    )
                now = time()
                res = (
                        f"{chat_wrapper.get_chatbot().chat(context).wait_until_done()}\n\n"
                        f"Response time: {time() - now:.2f} seconds\n"
                        f"References:\n{"\n".join([f"{i+1}. https://{SLACK_WORKSPACE_NAME}.slack.com/archives/{item['properties']['channel_id']}/p{item['properties']['thread_ts'].replace('.', '')}?thread_ts={item['properties']['thread_ts'].replace('.', '')}&cid={item['properties']['channel_id']}" for i, item in enumerate(retrieved_data)])}\n"
                )
            else:
                res = (
                    'Please use one of the following prefixes:\n'
                    '"Echo:",\n' 
                    '"Chat:"\n'
                )
        say(res)


fastapi_app = FastAPI()

handler = SlackRequestHandler(app)

@fastapi_app.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)

@fastapi_app.get("/")
def ping():
    return {"response": "SlackBot is running!"} 


if __name__ == "__main__":
    import uvicorn
    import signal
    import sys

    def cleanup(signum=None, frame=None):
        print("Signal received, shutting down gracefully...")
        retriever.weaviate_client.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)  # Handles Ctrl+C
    signal.signal(signal.SIGTERM, cleanup)  # Handles process termination

    try:
        retriever = Retriever()
        if not retriever.check_connection():
            for _ in range(5):
                if not retriever.client_reconnect():
                    print("Failed to reconnect to Weaviate client. Retrying...")
                    sleep(2)
                else:
                    break

        uvicorn.run(fastapi_app, host="0.0.0.0", port=50001)
    except KeyboardInterrupt:
        cleanup()