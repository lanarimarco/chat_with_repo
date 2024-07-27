import os
from dotenv import load_dotenv

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google settings
# Client ID and secret are stored in the client_secret.json
# Google project: https://console.cloud.google.com/apis/credentials?project=chatwithrepo-429720
# Account: lanarimarco@gmail.com
# Credenziali -> ID client OAuth 2.0 - development
CLIENT_SECRET_PATH = os.path.join(os.getcwd(), "client_secret.json")

SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]
##########################################################################

AUTHORAZED_USERS = os.getenv("AUTHORIZED_USERS")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

## Validation

if not GITHUB_TOKEN:
    raise Exception(
        "Wrong github settings. GITHUB_TOKEN environment variable is not set."
    )

if not OPENAI_API_KEY:
    raise Exception(
        "Wrong openai settings. OPENAI_API_KEY environment variable is not set."
    )

if not os.path.exists(CLIENT_SECRET_PATH):
    raise Exception(f"Wrong google auth settings. {CLIENT_SECRET_PATH} file not found.")

if not AUTHORAZED_USERS:
    raise Exception(
        "Wrong authorized users settings. AUTHORIZED_USERS environment variable is not set."
    )

if not MODEL_NAME:
    raise Exception(
        "Wrong model settings. MODEL_NAME environment variable is not set."
    )
