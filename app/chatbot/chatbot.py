import os
from dotenv import load_dotenv
from hugchat import hugchat
from hugchat.login import Login
import openai

from typing import Union, Literal

class HuggingChatWrapper:
    def __init__(self):
        """Initialize the HuggingChatWrapper class and load environment variables."""
        # Load environment variables
        load_dotenv()

        # Fetch environment variables
        self.__email = os.getenv("HUGGINGFACE_EMAIL")
        self.__password = os.getenv("HUGGINGFACE_PASSWORD")
        self.__cookie_path_dir = os.getenv("HUGGINGFACE_COOKIE_DIR")
        

        if not self.__email or not self.__password:
            raise ValueError("Missing HUGGINGFACE_EMAIL or HUGGINGFACE_PASSWORD in environment variables.")
        
        self._chatbot_instance = None  # Singleton instance placeholder
        print("initialized NEW HuggingChatWrapper")

    def get_chatbot(self) -> hugchat.ChatBot:
        """Initialize and return a singleton instance of the ChatBot."""
        if self._chatbot_instance is None:
            try:
                # Authenticate and store the cookies
                sign = Login(self.__email, self.__password)
                cookies = sign.login()
                self._chatbot_instance = hugchat.ChatBot(
                    cookies=cookies.get_dict(),
                    default_llm="meta-llama/Llama-3.3-70B-Instruct"
                )
                print("initialized a NEW hugchat ChatBot")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Hugging Face ChatBot: {e}")
        return self._chatbot_instance

class OpenAIChatWrapper:
    def __init__(self):
        """Initialize the OpenAIChatWrapper class and load environment variables."""
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.model = os.getenv("OPENAI_MODEL", "nim-mistral-7b-instruct")

        if not self.api_key or not self.base_url:
            raise ValueError("Missing OPENAI_API_KEY or OPENAI_BASE_URL in environment variables.")
        
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, message: str):
        """Send a chat request to the OpenAI-compatible API, formatting input appropriately."""
        messages = [{"role": "user", "content": message}]
        response = self.client.chat.completions.create(model=self.model, messages=messages)
        return response

class ChatClient:
    def __init__(self, provider: Union[Literal["huggingface"], Literal["openai"]] = "huggingface"):
        """
        Initialize ChatClient with a selected provider.

        Args:
            provider (Union[Literal["huggingface"], Literal["openai"]], optional): 
                The chatbot provider to use. Defaults to "huggingface".
                Options:
                    - "huggingface": Use the HuggingChatWrapper.
                    - "openai": Use the OpenAIChatWrapper.

        Raises:
            ValueError: If an unsupported provider is specified.
        """
        if provider == "huggingface":
            self.chatbot = HuggingChatWrapper().get_chatbot()
        elif provider == "openai":
            self.chatbot = OpenAIChatWrapper()
        else:
            raise ValueError("Unsupported provider. Choose 'huggingface' or 'openai'.")

    def chat(self, message: str):
        """Send a chat request based on the selected provider."""
        return self.chatbot.chat(message)
