from typing import Callable
from chat_with_repo import OPENAI_API_KEY
from chat_with_repo.commit_tools import (
    GetCommitsByPathTool,
    GetCommitsByPullRequestTool,
)
from chat_with_repo.misc_tools import SelectGitHubRepoTool
from chat_with_repo.model import State
from chat_with_repo.pull_request_tools import (
    GetPullRequestByNumberTool,
    GetPullRequestsByCommitTool,
    GetPullRequestByPathTool,
)
from chat_with_repo.pull_request_tools import (
    GetPullRequestsTool,
)


from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


from collections import deque


class GitHubAssistant:

    def __init__(
        self,
        owner: str = "smeup",
        repo: str = "jariko",
        model: str = "gpt-3.5-turbo",
        chat_history_length: int = 10,
        topK: int = 10,
        on_change_repo: Callable[[str], None] = None,
    ):
        """
        Initializes a new instance of the GitHubAssistant class.
        args:
            owner: The owner of the GitHub repository. Defaults to "smeup".
            repo: The name of the GitHub repository. Defaults to "jariko".
            model: The OpenAI model to use for the assistant. Defaults to "gpt-3.5-turbo".
            chat_history_length: The maximum number of chat messages to keep in the chat history. Defaults to 10.
            topK: The maximum number of results to return from the GitHub API.
            on_change_repo: A callback function that is called when the repository is changed.
        """
        if not owner:
            raise ValueError("owner must be specified")
        if not repo:
            raise ValueError("repo must be specified")
        if not model:
            raise ValueError("model must be specified")
        self.model = model
        self.chat_history = deque(maxlen=chat_history_length)
        self.topK = topK
        self.state = State()
        self.on_change_repo = on_change_repo

    system = """
    You are a virtual assistant that helps with GitHub-related tasks.
    For each task you will use a tool.
    If are not able to find the task related to the user's question, you must show to the user a message where you will show all tools available with a brief description.
    If the user asks if a branch is merged to another branch, you must answer by using tool: 'get_pull_requests'.
    If the answer is retrieved by tool you must show to the user only the information retrieved by the tool, nothing more.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    def new_thread(self):
        self.chat_history.clear()

    def chat(self, message: str) -> str:
        self.state.on_change_repo = lambda repo: self.__on_change_repo(repo)
        llm = ChatOpenAI(model=self.model, temperature=0, api_key=OPENAI_API_KEY)
        if not self.state.is_repo_selected():
            tools = [SelectGitHubRepoTool(state=self.state)]
        else:
            tools = [
                SelectGitHubRepoTool(state=self.state),
                GetPullRequestByNumberTool(state=self.state, topK=self.topK),
                GetPullRequestsTool(state=self.state, topK=self.topK),
                GetPullRequestsByCommitTool(state=self.state, topK=self.topK),
                GetPullRequestByPathTool(state=self.state, topK=self.topK),
                GetCommitsByPathTool(state=self.state, topK=self.topK),
                GetCommitsByPullRequestTool(state=self.state, topK=self.topK),
            ]
        agent = create_openai_tools_agent(llm, tools, self.prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        agent_response = agent_executor.invoke(
            input={"input": message, "chat_history": list(self.chat_history)}
        )
        self.chat_history.append(HumanMessage(content=agent_response["input"]))
        self.chat_history.append(AIMessage(content=agent_response["output"]))
        return agent_response["output"]

    def __on_change_repo(self, new_repo: str):
        if self.on_change_repo is not None:
            self.on_change_repo(new_repo)
        self.new_thread()
