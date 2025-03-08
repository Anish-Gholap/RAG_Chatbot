# config.py
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# LangSmith configuration
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "default")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"