from datetime import datetime
from typing import Callable, List, Optional
from pydantic import BaseModel
from enum import Enum
from langchain_core.messages import BaseMessage


class Repo(Enum):

    chat_with_repo = "chat_with_repo"

    jariko = "jariko"
    jardis = "jardis"
    ketchup = "ketchup"
    kokos = "kokos"
    kokos_me_node_gibus = "kokos-me-node-gibus"
    kokos_sdk_java_rpgle = "kokos-sdk-java-rpgle"
    reload = "reload"
    webup_project = "webup-project"
    webup_js = "webup.js"

    @property
    def owner(self):
        if self == Repo.chat_with_repo:
            return "lanarimarco"
        else:
            return "smeup"

    @staticmethod
    def to_str():
        return ", ".join([member.value for member in Repo])


class State:
    def __init__(self, repo: Repo = Repo.jariko, messages: List[BaseMessage] = []):
        """Initializes a new instance of the State

        Args:
            repo (Repo, optional): The repository. Defaults to Repo.jariko.
            messages (List[BaseMessage], optional): The messages at agent execution time (before the agent is invoked). Defaults to [].
        """
        self._repo: Repo = repo
        self.on_change_repo: Callable[[Repo], None] = None
        self.messages: List[BaseMessage] = messages

    def is_repo_selected(self):
        return self.repo is not None

    @property
    def repo(self) -> Repo:
        return self._repo

    @repo.setter
    def repo(self, value: Repo):
        changed = self._repo != value
        self._repo = value
        if changed and self.on_change_repo is not None:
            self.on_change_repo(value)


class Head(BaseModel):
    label: str
    ref: str
    sha: str


class User(BaseModel):
    login: str


class PullRequest(BaseModel):
    number: int
    html_url: str
    diff_url: str
    title: str
    user: User
    body: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    head: Head
    base: Head


class Author(BaseModel):
    name: str
    email: str
    date: datetime


class CommitDetail(BaseModel):
    author: Author
    message: str


class Commit(BaseModel):
    sha: str
    html_url: str
    commit: CommitDetail


class FileChange(BaseModel):
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int


class CommitFilter(BaseModel):
    """
    Represents a filter for querying commits.

    Attributes:
        sha (Optional[str]): SHA or branch to start listing commits from. Default: the repository’s default branch (usually main).
        path (Optional[str]): Only commits containing this file path will be returned.
        author (Optional[str]): GitHub username or email address to use to filter by commit author.
        committer (Optional[str]): GitHub username or email address to use to filter by commit committer.
    """

    sha: Optional[str] = None
    path: Optional[str] = None
    author: Optional[str] = None
    committer: Optional[str] = None


class PullRequestState(Enum):
    OPENED = "opened"
    CLOSED = "closed"
    ALL = "all"


class PullRequestFilter(BaseModel):
    """
    Represents a filter for querying pull requests.

    Attributes:
        title (Optional[str]): The pull request title.
        body (Optional[str]): The pull request body.
        opened_from_branch (Optional[str]): The branch from which the pull request was opened.
        target_branch (str): The target branch of the pull request. Defaults to "develop".
        state (PullRequestState): The state of the pull request. Defaults to PullRequestState.ALL.
    """

    title: Optional[str] = None
    body: Optional[str] = None
    opened_from_branch: Optional[str] = None
    target_branch: str = "develop"
    state: PullRequestState = PullRequestState.ALL
