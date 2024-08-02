import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
import requests

from chat_with_repo import CLIENT_SECRET, DEBUG, REDIRECT_URI, SCOPES
from chat_with_repo.users import User

__debug_user = User(email="debuguser@debug.it", name="Debug User", avatar="😎")


def get_user() -> User:
    if DEBUG:
        return __debug_user
    if st.session_state.get("user", ""):
        return st.session_state["user"]
    else:
        if st.query_params.get("code", ""):
            __handle_auth_response()
            st.session_state["authenticated"] = True
            return st.session_state["user"]
        if st.button("Login with Google"):
            __redirect_to_auth()


def __create_flow() -> InstalledAppFlow:
    flow = InstalledAppFlow.from_client_config(CLIENT_SECRET, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    return flow


# Redirect user to Google's OAuth 2.0 server
def __redirect_to_auth():
    # Create the OAuth flow object
    flow = __create_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline", prompt="select_account"
    )
    st.markdown(
        f'<meta http-equiv="refresh" content="0;URL={authorization_url}">',
        unsafe_allow_html=True,
    )
    # st.write(f"Please go to this URL and authorize access: {authorization_url}")


# Handle the OAuth 2.0 server response
def __handle_auth_response():
    flow = __create_flow()
    flow.fetch_token(code=st.query_params["code"])
    credentials = flow.credentials
    access_token = credentials.token
    user_info_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"

    response = requests.get(
        user_info_endpoint, headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code == 200:
        user_info = response.json()
        avatar = requests.get(
            user_info.get("picture"),
            headers={"Authorization": f"Bearer {access_token}"},
        ).content
        user = User(
            email=user_info.get("email"), name=user_info.get("name"), avatar=avatar
        )
        st.session_state["user"] = user
    else:
        st.error(f"Failed to fetch user info: {response.text}")


def custom_request(url, method="GET", **kwargs):
    response = requests.request(method, url, **kwargs)
    response.status = response.status_code
