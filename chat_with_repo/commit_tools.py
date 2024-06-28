from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from chat_with_repo import GITHUB_TOKEN
from chat_with_repo.model import Commit, CommitFilter


import requests


from typing import Callable, List, Type


class GetCommitsByPathSchema(BaseModel):
    path: str = Field(..., description="The path to the file.")


class GetCommitsByPathTool(BaseTool):
    owner: str
    repo: str
    topK: int = 10
    args_schema: Type[BaseModel] = GetCommitsByPathSchema
    name: str = "get_commits_by_path"
    description = "Retrieves a list of commits associated with a specific file."

    def _run(self, path: str) -> List[Commit]:
        return get_commits_by_path(path=path, owner=self.owner, repo=self.repo)[
            : self.topK
        ]


class IsCommitInBranchSchema(BaseModel):
    commit_sha: str = Field(..., description="The SHA of the commit.")
    branch: str = Field(..., description="The name of the branch.")


class IsCommitInBranchTool(BaseTool):
    owner: str
    repo: str
    args_schema: Type[BaseModel] = IsCommitInBranchSchema
    name: str = "is_commit_in_branch"
    description = "Checks if a commit is in a given branch."

    def _run(self, commit_sha: str, branch: str) -> bool:
        return is_commit_in_branch(commit_sha, branch, owner=self.owner, repo=self.repo)


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


def is_commit_in_branch(
    commit_sha: str, branch: str, owner: str = "smeup", repo: str = "jariko"
) -> bool:
    """
    Checks if a commit is in a given branch.

    Args:
        commit_sha (str): The SHA of the commit.
        branch (str): The name of the branch.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        bool: True if the commit is in the branch, False otherwise.
    """
    matched = False

    def exit_condition(commit: Commit):
        nonlocal matched
        if commit.sha == commit_sha:
            matched = True
            return True
        return False

    __get_commits(
        commit_filter=CommitFilter(sha=branch),
        owner=owner,
        repo=repo,
        exit_condition=exit_condition,
    )

    return matched


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
