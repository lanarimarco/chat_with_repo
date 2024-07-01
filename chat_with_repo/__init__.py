import os
from dotenv import load_dotenv

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GITHUB_TOKEN:
    raise Exception("GITHUB_TOKEN environment variable is not set.")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY environment variable is not set.")
