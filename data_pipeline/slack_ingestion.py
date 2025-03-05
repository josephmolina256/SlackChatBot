from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request

from typing import Optional
import os
import traceback
from time import sleep

from dotenv import load_dotenv

from .constants import APPROVED_USER_GROUP, APPROVED_REACTIONS
from .store import Storer


load_dotenv(override=True)

fastapi_app = FastAPI()


app = App(token=os.environ.get("SLACK_INGESTION_BOT_TOKEN"), signing_secret=os.environ.get("INGESTION_SIGNING_SECRET"))
handler = SlackRequestHandler(app)
approved_user_set = set()

def set_approved_users(approver_usergroup_name: str) -> Optional[str]:
    global approved_user_set
    response = app.client.usergroups_list()
    usergroups = response.get("usergroups", [])

    usergroup_id = None

    for ug in usergroups:
        if ug["name"] == approver_usergroup_name:
            usergroup_id = ug["id"]
            break
    if usergroup_id:
        l = app.client.usergroups_users_list(usergroup=usergroup_id)
        approved_user_set = set(l.get("users", []))
        return True
    else:
        return False

@app.event("reaction_added")
def handle_reaction(event):
    try:    
        if event.get("user") in approved_user_set:
            if event.get("reaction") in APPROVED_REACTIONS:
                print("Approved!")
                print(event)

                # get the message that was reacted to
                channel_id = event.get("item").get("channel")
                reply_ts = event.get("item").get("ts")
                reply_with_metadata = app.client.conversations_replies(channel=channel_id, ts=reply_ts).get("messages", ["Invalid message"])[0]
                reply_client_msg_id = reply_with_metadata.get("client_msg_id")
                print(reply_with_metadata)

                # check if the message is a reply to a thread or a standalone message
                thread_messages = []
                if reply_with_metadata == "Invalid message":
                    print("Invalid message.")
                    return
                elif "parent_user_id" in reply_with_metadata:
                    head_thread_ts = reply_with_metadata.get("thread_ts")
                    slack_response = app.client.conversations_replies(channel=channel_id, ts=head_thread_ts)
                    head_message = slack_response.get("messages", ["Invalid message"])[0]
                    if head_message == "Invalid message":
                        print("Invalid head message.")
                        return
                    
                    thread_messages = [
                        head_message,
                        reply_with_metadata 
                    ]
                else:
                    print("Not a reply to a thread, storing as a standalone message.")
                    thread_messages = [
                        reply_with_metadata
                    ]
                #TODO: Think about batching for the future
                threads = [
                    {
                        "head": thread_messages[0].get("text"),
                        "responses": thread_messages[1].get("text") if len(thread_messages) > 1 else None,
                        "thread_ts": reply_ts,
                        "channel_id": channel_id,
                        "uuid": reply_client_msg_id
                    }
                ]
                storer.store(threads)
            else:
                print("Irrelevant reaction.")
        else:
            print("Not approved!")
    except Exception as e:
        print("An error occurred in handle_reaction: ")
        traceback.print_exc()  # Prints full traceback

@fastapi_app.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)

@fastapi_app.get("/")
def ping():
    return {"response": "Ingestion service is running!"}


if __name__ == "__main__":
    import uvicorn
    import signal
    import sys

    def cleanup(signum=None, frame=None):
        print("Signal received, shutting down gracefully...")
        # storer.weaviate_client.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)  # Handles Ctrl+C
    signal.signal(signal.SIGTERM, cleanup)  # Handles process termination

    try:
        assert set_approved_users(APPROVED_USER_GROUP)
        storer = Storer()
        if not storer.check_connection():
            for _ in range(5):
                if not storer.client_reconnect():
                    print("Failed to reconnect to Weaviate client. Retrying...")
                    sleep(2)
                else:
                    break
        uvicorn.run(fastapi_app, host="0.0.0.0", port=40001)
    except KeyboardInterrupt:
        cleanup()