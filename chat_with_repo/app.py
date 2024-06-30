import streamlit as st
from chat_with_repo.assistant import GitHubAssistant
from enum import Enum


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

    global repo

    st.title("Chat with smeup repo")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "assistant" not in st.session_state:
        st.session_state.assistant = GitHubAssistant()



    repo = st.session_state.assistant.state.repo

    assistant: GitHubAssistant = st.session_state.assistant


    # # Display chat messages from history on app rerun
    # for message in st.session_state.messages:
    #     if message["role"] == Role.USER.value:
    #         with st.chat_message(Role.USER.value, avatar=Role.USER.avatar):
    #             st.markdown(message["content"])
    #     else:
    #         with st.chat_message(Role.ASSISTANT.value, avatar=Role.ASSISTANT.avatar):
    #             st.markdown(message["content"])
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Hello, how can I help you?"):
        # Display user message in chat message container
        with st.chat_message(Role.USER.value):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": Role.USER.value, "content": prompt})

        response = st.session_state.assistant.chat(prompt)
        # Display assistant response in chat message container
        with st.chat_message(name=assistant.state.repo):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": repo, "content": response})


def process_message(message):
    # Add your logic here to process the user's message and generate a response
    # For example, you could use a chatbot library or an API to generate the response
    # In this example, we'll just echo the user's message
    return message


if __name__ == "__main__":
    main()
