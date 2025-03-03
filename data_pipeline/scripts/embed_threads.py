import json
from sentence_transformers import SentenceTransformer
import sqlite3

conn = sqlite3.connect('./data/slack_threads.db')
cursor = conn.cursor()
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_qa_data(input_file_path="./data/qa_store.json", output_file_path="./data/slack_threads.db"):
    try:
        with open(input_file_path, "r") as file:
            qa_data = json.load(file)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS thread_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT UNIQUE,
            answer TEXT,
            channel_id TEXT,
            thread_ts TEXT,
            embedding TEXT
        )
        """)
        for qa_item in qa_data:
            cursor.execute(
                """
                INSERT OR IGNORE INTO thread_data (question, answer, channel_id, thread_ts, embedding)
                VALUES (?, ?, ?, ?, ?)
                """, 
                (
                    qa_item["question"],
                    qa_item["answer"],
                    qa_item["channel_id"],
                    qa_item["thread_ts"],
                    json.dumps(
                        embedding_model.encode(qa_item["question"]).tolist()
                        )
                )
            )
            conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False 
    

def main():
    embed_qa_data()



if __name__ == "__main__" :
    main()