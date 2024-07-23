import streamlit as st
from chat_with_repo.assistant import GitHubAssistant
from enum import Enum

from chat_with_repo.auth2 import get_user


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"

    @property
    def avatar(self):
        if self == Role.USER:
            return "https://avatars.githubusercontent.com/u/40103274?s=96&v=4"
        elif self == Role.ASSISTANT:
            return "https://raw.githubusercontent.com/smeup/jariko/develop/images/jariko_small.png"


def main():

    st.title("Chat with smeup repo")

    user = get_user()

    if user is not None:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "assistant" not in st.session_state:
            st.session_state.assistant = GitHubAssistant()

        assistant: GitHubAssistant = st.session_state.assistant

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            if message["role"] == user.name:
                with st.chat_message(user.name, avatar=user.avatar):
                    st.markdown(message["content"])
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input(f"Hello {user.email} how can I help you?"):
            # Display user message in chat message container
            with st.chat_message(user.name, avatar=user.avatar):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": user.name, "content": prompt})

            response = st.session_state.assistant.chat(prompt)
            # Display assistant response in chat message container
            with st.chat_message(name=assistant.state.repo.value):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": assistant.state.repo.value, "content": response}
            )


def process_message(message):
    # Add your logic here to process the user's message and generate a response
    # For example, you could use a chatbot library or an API to generate the response
    # In this example, we'll just echo the user's message
    return message


if __name__ == "__main__":
    main()
