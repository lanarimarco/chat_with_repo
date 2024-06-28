from chat_with_repo import OPENAI_API_KEY
from chat_with_repo.commit_tools import (
    GetCommitsByPathTool,
    IsCommitInBranchTool,
)
from chat_with_repo.model import State
from chat_with_repo.pull_request_tools import (
    GetPullRequestByCommitTool,
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
    ):
        """
        Initializes a new instance of the GitHubAssistant class.

        Args:
            owner (str): The owner of the GitHub repository. Defaults to "smeup".
            repo (str): The name of the GitHub repository. Defaults to "jariko".
            model (str): The name of the GPT model to use. Defaults to "gpt-3.5-turbo".
            chat_history_length (int): The maximum length of the chat history. Defaults to 10.
            topK (int): The number of top results to return. Defaults to 10.
        """
        self.model = model
        self.chat_history = deque(maxlen=chat_history_length)
        self.topK = topK
        self.state = State(owner=owner, repo=repo)

    system = """
    You are a virtual assistant that helps with GitHub-related tasks.
    For each task you will use a tool.
    If are not able to find the task related to the user's question, you must show to the user a message where you will show all tools available with a brief description.
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
        llm = ChatOpenAI(model=self.model, temperature=0, api_key=OPENAI_API_KEY)
        tools = [
            GetPullRequestsTool(
                repo=self.state.repo, owner=self.state.owner, topK=self.topK
            ),
            GetPullRequestByCommitTool(
                repo=self.state.repo, owner=self.state.owner, topK=self.topK
            ),
            GetPullRequestByPathTool(
                repo=self.state.repo, owner=self.state.owner, topK=self.topK
            ),
            GetCommitsByPathTool(
                repo=self.state.repo, owner=self.state.owner, topK=self.topK
            ),
            IsCommitInBranchTool(repo=self.state.repo, owner=self.state.owner),
        ]
        agent = create_openai_tools_agent(llm, tools, self.prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        agent_response = agent_executor.invoke(
            input={"input": message, "chat_history": list(self.chat_history)}
        )
        self.chat_history.append(HumanMessage(content=agent_response["input"]))
        self.chat_history.append(AIMessage(content=agent_response["output"]))
        return agent_response["output"]
