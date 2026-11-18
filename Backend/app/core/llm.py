import os

from dotenv import load_dotenv
from langchain.agents.middleware import ModelRetryMiddleware
from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai.chat_models import GoogleRateLimitError

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

model = init_chat_model("google_genai:" + MODEL_NAME)

retry = ModelRetryMiddleware(max_retries=4, retry_on=(GoogleRateLimitError,), on_failure="error", initial_delay=15, max_delay=60)

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", output_dimensionality=768)
