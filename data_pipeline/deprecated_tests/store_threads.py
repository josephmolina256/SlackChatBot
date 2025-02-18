from slack_sdk import WebClient
import os
import json
from dotenv import load_dotenv

class slackThreadHandler():
    def __init__(self):
        load_dotenv()
        self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.threads_queue = []

    def _get_last_n_messages(self, channel_id, n=10):
        """Fetches the last N messages from a Slack channel."""
        response = self.client.conversations_history(channel=channel_id, limit=n)
        messages = response.get("messages", [])
        
        return messages

    def _get_thread_messages(self, channel_id, thread_ts):
        """Fetches the full thread for a given thread timestamp (ts)."""
        response = self.client.conversations_replies(channel=channel_id, ts=thread_ts)
        return response.get("messages", [])

    def queue_threads(self, channel_id, n=10):
        """Fetches the last N messages, expands threads, and groups them together."""
        messages = self._get_last_n_messages(channel_id, n)
        
        grouped_messages = []  # List to hold formatted conversation groups
        seen_threads = set()   # Track threads to avoid duplicate retrieval

        for message in messages:
            thread_ts = message.get("thread_ts", message["ts"])  # Use thread_ts if exists, otherwise ts
            if thread_ts in seen_threads:
                continue  # Skip messages already processed in a thread
            
            seen_threads.add(thread_ts)

            if "thread_ts" in message:
                thread_messages = self._get_thread_messages(channel_id, thread_ts)
            else:
                continue # Standalone message

            thread_group = {
                "head_message": thread_messages[0].get("text"),
                "checked_replies": [],
                "thread_ts": thread_ts
            }

            if len(thread_messages) > 1:
                for i in range(1,len(thread_messages)):
                    msg = thread_messages[i]
                    reaction_set = {reaction["name"] for reaction in msg.get("reactions", [])}
                    if reaction_set and "white_check_mark" in reaction_set:
                        thread_group["checked_replies"].append(msg.get('text'))
            if len(thread_group["checked_replies"]) > 0:
                grouped_messages.append(thread_group)

        #TODO: Make a peristent queue
        self.threads_queue = grouped_messages
        return grouped_messages


    def process_threads(self, channel_id, number_of_messages=1, output_file_path=None):
        if len(self.threads_queue) > 0:
            threads = self.threads_queue
        else:
            print("Need to add threads to queue first!")
            return
        qa_set = []
        # Uncomment to make items persist
        # with open(output_file_path, "r") as file:
        #     qa_set = json.load(file)

        for thread in threads:
            print("Head:", thread.get("head_message"))
            print("Checked replies:", thread.get("checked_replies"))
            if input("Do you want to store this thread? (y/n): ").lower() == 'y':
                qa_set.append(
                    {
                        "question": thread.get("head_message"),
                        "answer": "Answer: " + "\nAnswer: ".join(thread.get("checked_replies")),
                        "channel_id": channel_id,
                        "thread_ts": thread["thread_ts"]  # Use thread_ts if exists, otherwise ts
                    }
                )
            else:
                continue

        with open(output_file_path, "w") as file:
            json.dump(qa_set, file, indent=4)

CHANNEL_ID="C06TPPJ49GV"
OUTPUT_FILE_PATH="./data/qa_store.json"
def main():
    slack_handler = slackThreadHandler()
    slack_handler.queue_threads(channel_id=CHANNEL_ID)
    slack_handler.process_threads(channel_id=CHANNEL_ID, output_file_path=OUTPUT_FILE_PATH)


if __name__ == "__main__" :
    main()
