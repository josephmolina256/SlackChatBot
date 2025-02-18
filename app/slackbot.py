from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from time import time

from .chatbot.chatbot import HuggingChatWrapper
from data_pipeline.retrieve import Retriever


load_dotenv(override=True)

chat_wrapper = HuggingChatWrapper() # Singleton chat wrapper
chatbot = chat_wrapper.get_chatbot()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SIGNING_SECRET"))

retriever = Retriever()


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
                        f"References:\n{"\n".join([f"{i}. https://sfomttir.slack.com/archives/{item['properties']['channel_id']}/p{item['properties']['thread_ts'].replace('.', '')}" for i, item in enumerate(retrieved_data)])}\n"
                )
            else:
                res = (
                    'Please use one of the following prefixes:\n'
                    '"Echo:",\n' 
                    '"Chat:"\n'
                )
        say(res)


@app.event("app_mention")
def handle_bot_practice_channel_messages(event, say):
    """Handles messages where the bot is mentioned in the 'random' channel and replies in a thread."""
    user_message = event.get("text")
    user_id = event.get("user")

    # Use 'thread_ts' if it's provided, otherwise, reply in a new thread
    thread_ts = event.get("thread_ts") or event.get("ts")  

    say(
        text=f"Hello <@{user_id}>, you said: {user_message}",
        thread_ts=thread_ts  # Reply in the same thread
    )


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

    # Handle Ctrl+C and termination signals
    signal.signal(signal.SIGINT, cleanup)  # Handles Ctrl+C
    signal.signal(signal.SIGTERM, cleanup)  # Handles process termination

    # Main application loop (example)
    try:
        uvicorn.run(fastapi_app, host="0.0.0.0", port=50001)
    except KeyboardInterrupt:
        cleanup()