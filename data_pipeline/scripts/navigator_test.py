import openai
import os
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("NAVIGATOR_API_KEY"),
    base_url="https://api.ai.it.ufl.edu/v1"
)

response = client.models.list()
print(response)