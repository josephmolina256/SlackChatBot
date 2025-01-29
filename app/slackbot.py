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

@app.event("message")
def handle_message(event, say):
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

fastapi_app = FastAPI()

handler = SlackRequestHandler(app)

@fastapi_app.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=3000)
