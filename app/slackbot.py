from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request

import os
import json
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

@app.event("message")
def handle_message(event, say):
    print("received event!")
    if event.get("channel_type") == "im":
        user_message = event.get("text")
        user_id = event.get("user")
        res = ""
        if user_message and type(user_message) == str:
            if user_message.startswith("Echo:"):
                res = f"Hey <@{user_id}>, you said: {user_message[5:]}"
            elif user_message.startswith("Chat:"):
                print("Generating a response...")
                res = chat_wrapper.get_chatbot().chat(user_message).wait_until_done()  # Blocking call to LLM
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
