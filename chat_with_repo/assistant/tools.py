from typing import Type
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

from chat_with_repo.model import PullRequestFilter, PullRequestState
from chat_with_repo.tools import (
    get_commits_by_path,
    get_pull_requests,
    get_pull_requests_by_commit,
    get_pull_requests_by_path,
)


class GetPullRequestByCommitShema(BaseModel):
    commit_sha: str = Field(..., description="The SHA of the commit.")


class GetPullRequestByCommitTool(BaseTool):
    owner: str
    repo: str
    topK: int = 10
    args_schema: Type[BaseModel] = GetPullRequestByCommitShema
    name: str = "get_pull_requests_by_commit"
    description = "Retrieves a list of pull requests associated with a specific commit."

    def _run(self, commit_sha: str):
        return get_pull_requests_by_commit(
            commit_sha=commit_sha, owner=self.owner, repo=self.repo
        )[: self.topK]


class GetCommitByPathSchema(BaseModel):
    path: str = Field(..., description="The path to the file.")


class GetCommitByPathTool(BaseTool):
    owner: str
    repo: str
    topK: int = 10
    args_schema: Type[BaseModel] = GetCommitByPathSchema
    name: str = "get_commits_by_path"
    description = "Retrieves a list of commits associated with a specific file."

    def _run(self, path: str):
        return get_commits_by_path(path=path, owner=self.owner, repo=self.repo)[
            : self.topK
        ]


class GetPullRequestByPathSchema(BaseModel):
    path: str = Field(..., description="The path to the file.")


class GetPullRequestByPathTool(BaseTool):
    owner: str
    repo: str
    topK: int = 10
    args_schema: Type[BaseModel] = GetPullRequestByPathSchema
    name: str = "get_pull_requests_by_path"
    description = "Retrieves a list of pull requests associated with a specific file."

    def _run(self, path: str):
        return get_pull_requests_by_path(path=path, owner=self.owner, repo=self.repo)[
            : self.topK
        ]


class GetPullRequestsSchema(BaseModel):
    number: int = Field(description="The pull request number.", default=None)
    title: str = Field(description="The title of the pull request.", default=None)
    body: str = Field(
        description="The body or description of the pull request.", default=None
    )
    opened_from_branch: str = Field(
        description="The branch for which the user asks question.", default=None
    )
    target_branch: str = Field(
        description="The target branch of the pull request.", default="develop"
    )
    state: PullRequestState = Field(
        description="The state of the pull request.", default=PullRequestState.ALL
    )


class GetPullRequestsTool(BaseTool):
    owner: str
    repo: str
    topK: int = 10
    args_schema: Type[BaseModel] = GetPullRequestsSchema
    name: str = "get_pull_requests"
    description = "Retrieves a list of pull requests based on the provided filters."

    def _run(
        self,
        number: int = None,
        title: str = None,
        body: str = None,
        opened_from_branch: str = None,
        target_branch: str = "develop",
        state: PullRequestState = PullRequestState.ALL,
    ):
        return get_pull_requests(
            PullRequestFilter(
                number=number,
                title=title,
                body=body,
                opened_from_branch=opened_from_branch,
                target_branch=target_branch,
                state=state,
            ),
            owner=self.owner,
            repo=self.repo,
        )[: self.topK]
