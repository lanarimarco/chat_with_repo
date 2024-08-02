import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Google settings
# Client ID and secret are stored in the client_secret.json
# Google project: https://console.cloud.google.com/apis/credentials?project=chatwithrepo-429720
# Account: lanarimarco@gmail.com
# Credenziali -> ID client OAuth 2.0 - development
CLIENT_SECRET: dict[str, any] = st.secrets["google"]["client_secret"]


SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

REDIRECT_URI = st.secrets["google"]["flow"]["redirect_uri"]
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

if not CLIENT_SECRET:
    raise Exception(
        "Wrong google auth settings. CLIENT_SECRET is not set. "
        "In local development you can set it in the .streamlit/secrets.toml section: [google.client_secret.web], view .secrets.toml for further information. "
        "In production you can set it in the environment variables."
    )
if not REDIRECT_URI:
    raise Exception(
        "Wrong google auth settings. REDIRECT_URI is not set. "
        "In local development you can set it in the .streamlit/secrets.toml section: [google.flow.redirect_uri], view .secrets.toml for further information. "
        "In production you can set it in the environment variables."
    )

if not AUTHORAZED_USERS:
    raise Exception(
        "Wrong authorized users settings. AUTHORIZED_USERS environment variable is not set."
    )

if not MODEL_NAME:
    raise Exception("Wrong model settings. MODEL_NAME environment variable is not set.")
