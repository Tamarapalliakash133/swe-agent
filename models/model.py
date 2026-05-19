from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment. Please set it in your .env file.")


def gpt_model():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3)
    return llm
