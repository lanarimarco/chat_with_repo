from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from chat_with_repo import GITHUB_TOKEN
from chat_with_repo.model import Commit, CommitFilter, Repo, State


import requests


from typing import Callable, List, Type


class GetCommitsByPathSchema(BaseModel):
    path: str = Field(..., description="The path to the file.")


class GetCommitsByPathTool(BaseTool):
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = GetCommitsByPathSchema
    name: str = "get_commits_by_path"
    description = "Retrieves a list of commits associated with a specific file."

    def _run(self, path: str) -> List[Commit]:
        return get_commits_by_path(path=path, owner=self.state.repo.owner, repo=self.state.repo.value)[
            : self.topK
        ]


class GetCommitsByPullRequestSchema(BaseModel):
    number: int = Field(..., description="The number of the pull request.")


class GetCommitsByPullRequestTool(BaseTool):
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = GetCommitsByPullRequestSchema
    name: str = "get_commits_by_pull_request"
    description = "Retrieves a list of commits associated with a specific pull request."

    def _run(self, number: int) -> List[Commit]:
        return get_commits_by_pull_request(
            number=number, owner=self.state.repo.owner, repo=self.state.repo.value
        )[: self.topK]


def get_commits_by_path(
    path: str, owner: str = "smeup", repo: str = "jariko"
) -> List[Commit]:
    """
    Retrieves the commits that have modified a given file.

    Args:
        path (str): The path of the file.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        List[Commit]: A list of Commit representing the retrieved commits.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    params = {
        "path": path,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return [Commit.model_validate(commit) for commit in response.json()]
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


def get_commits_by_pull_request(
    number: int, owner: str = "smeup", repo: str = "jariko"
) -> List[Commit]:
    """
    Retrieves the commits that have modified a given pull request.

    Args:
        number (int): The number of the pull request.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        List[Commit]: A list of Commit representing the retrieved commits.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}/commits"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [Commit.model_validate(commit) for commit in response.json()]
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


def __get_commits(
    commit_filter: CommitFilter = CommitFilter(),
    owner: str = "smeup",
    repo: str = "jariko",
    exit_condition: Callable[[Commit], bool] = lambda commit: False,
):
    """
    Retrieves commits from a GitHub repository.

    Args:
        commit_filter (CommitFilter, optional): A filter to apply to the commits. Defaults to CommitFilter().
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".
        exit_condition (Callable[[Commit], bool], optional): A function that determines when to stop processing commits.
            Defaults to lambda commit: False it means not exit.

    Raises:
        Exception: If there is an error in the API request.

    Returns:
        None
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    params = {"per_page": 100}
    if commit_filter.sha:
        params["sha"] = commit_filter.sha
    if commit_filter.path:
        params["path"] = commit_filter.path
    if commit_filter.author:
        params["author"] = commit_filter.author
    if commit_filter.committer:
        params["committer"] = commit_filter.committer
    response = requests.get(url, headers=headers, params=params)

    nextUrl = url

    while nextUrl:
        print(f"Processing {nextUrl}")
        response = requests.get(nextUrl, headers=headers, params=params)
        # Check if the request was successful
        if response.status_code == 200:
            nextUrl = response.links.get("next", {}).get("url")
            # Process the commits as needed
            for commit in response.json():
                if exit_condition(Commit.model_validate(commit)):
                    return
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
