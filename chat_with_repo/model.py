from datetime import datetime
from typing import Callable, Optional
from pydantic import BaseModel
from enum import Enum


class Repo(Enum):

    jariko = "jariko"
    kokos_sdk_java_rpgle = "kokos-sdk-java-rpgle"
    webup_project = "webup-project"
    webup_js = "webup.js"
    jardis = "jardis"
    chat_with_repo = "chat_with_repo"

    @property
    def owner(self):
        if self == Repo.chat_with_repo:
            return "lanarmarco"
        else:
            return "smeup"


class State:
    def __init__(self, repo: Repo = Repo.jariko):
        self._repo: Repo = repo
        self.on_change_repo: Callable[[Repo], None] = None

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
    url: str


class Commit(BaseModel):
    sha: str
    commit: CommitDetail


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
