from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from chat_with_repo import GITHUB_TOKEN
from chat_with_repo.model import Commit, CommitFilter, Repo, State


import requests


from typing import Callable, List, Optional, Type


class GetCommitByShaSchema(BaseModel):
    sha: str = Field(..., description="The SHA of the commit.")


class GetCommitByShaTool(BaseTool):
    state: State
    args_schema: Type[BaseModel] = GetCommitByShaSchema
    name: str = "get_commit_by_sha"
    description = "Retrieves a commit by its SHA and allows to answer to all questions related a commit identified  by a SHA."

    def _run(self, sha: str) -> Commit:
        return get_commit_by_sha(
            commit_sha=sha, owner=self.state.repo.owner, repo=self.state.repo.value
        )


class GetCommitsByPathSchema(BaseModel):
    path: str = Field(..., description="The path to the file.")


class GetCommitsByPathTool(BaseTool):
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = GetCommitsByPathSchema
    name: str = "get_commits_by_path"
    description = "Retrieves a list of commits associated with a specific file."

    def _run(self, path: str) -> List[Commit]:
        return get_commits_by_path(
            path=path, owner=self.state.repo.owner, repo=self.state.repo.value
        )[: self.topK]


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


class IsCommitInBaseSchema(BaseModel):
    commit_sha: str = Field(..., description="The commit SHA.")
    branch: str = Field(..., description="The branch name.")


class IsCommitInBaseTool(BaseTool):
    state: State
    args_schema: Type[BaseModel] = IsCommitInBaseSchema
    name: str = "is_commit_in_base"
    description = "Verifies if a commit is in a  hash, tag or branch name."

    def _run(self, commit_sha: str, branch: str) -> bool:
        return is_commit_in_base(
            commit_sha=commit_sha,
            base=branch,
            owner=self.state.repo.owner,
            repo=self.state.repo.value,
        )


class GetMergingCommitSchema(BaseModel):
    commit_sha: str = Field(..., description="The commit SHA.")
    branch: str = Field(..., description="The branch name.")


class GetMergingCommitTool(BaseTool):
    state: State
    args_schema: Type[BaseModel] = GetMergingCommitSchema
    name: str = "get_merging_commit"
    description = "Retrieves the commit that merged a given commit into a branch."

    def _run(self, commit_sha: str, branch: str) -> Optional[str]:
        return get_merging_commit(
            commit_sha=commit_sha,
            branch=branch,
            owner=self.state.repo.owner,
            repo=self.state.repo.value,
        )


def get_commit_by_sha(
    commit_sha: str, owner: str = "smeup", repo: str = "jariko"
) -> Optional[Commit]:
    """
    Retrieves a commit by its SHA.

    Args:
        commit_sha (str): The SHA of the commit.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        Commit: A Commit representing the retrieved commit.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return Commit.model_validate(response.json())
    elif response.status_code == 422:
        return None
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


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
    params = {
        "per_page": 100,
    }
    nextUrl = url
    commits = []
    while nextUrl:
        response = requests.get(nextUrl, headers=headers, params=params)
        if response.status_code == 200:
            nextUrl = response.links.get("next", {}).get("url")
            # Process the commits as needed
            for commit in response.json():
                commits.append(Commit.model_validate(commit))
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    return commits


# https://docs.github.com/rest/commits/commits#compare-two-commits
def compare_commits(
    base: str, head: str, owner: str = "smeup", repo: str = "jariko"
) -> Optional[List[Commit]]:
    """
    Retrieves the difference between two commits.

    Args:
        base (str): The base commit. Hash, tag or branch name.
        head (str): The head commit. Hash, tag or branch name.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        List[Commit]: A list of Commit representing the retrieved commits. If the base commit or the head commit does not exist,
        it returns None.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    params = {
        "per_page": 100,
    }

    nextUrl = url
    commits = []
    while nextUrl:
        response = requests.get(nextUrl, headers=headers, params=params)
        if response.status_code == 200:
            nextUrl = response.links.get("next", {}).get("url")
            # Process the commits as needed
            for commit in response.json()["commits"]:
                commits.append(Commit.model_validate(commit))
        elif response.status_code == 404:
            return None
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    return commits


def is_commit_in_base(
    commit_sha: str, base: str, owner: str = "smeup", repo: str = "jariko"
) -> bool:
    """
    Verifies if a commit is in a branch.

    Args:
        commit_sha (str): The commit SHA.
        base (str): The base commit. Hash, tag or branch name.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        bool: True if the commit is in the base, False otherwise.
    """
    commits = compare_commits(base=base, head=commit_sha, owner=owner, repo=repo)
    if commits is None:
        return False
    return not any(commit.sha == commit_sha for commit in commits)


def get_merging_commit(
    commit_sha: str, branch: str, owner: str = "smeup", repo: str = "jariko"
) -> Optional[Commit]:
    """
    It does now work properly. It should return the commit that merged the given commit into the branch,
    but actually it returns the parent commit of the given commit.
    Retrieves the commit that merged a given commit into a branch.

    Args:
        commit_sha (str): The commit SHA.
        branch (str): The branch name.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        Optional[Commit]: A Commit representing the retrieved commit. If the commit is not merged into the branch, it returns None.
    """
    # URL to check if the commit is in the branch
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"

    # Make the request
    response = requests.get(url)

    if response.status_code == 200:
        commit_data = response.json()
        # Loop through the parents of the commit
        for parent in commit_data["parents"]:
            parent_sha = parent["sha"]
            # Compare the parent commit with the branch
            compare_url = f"https://api.github.com/repos/{owner}/{repo}/compare/{branch}...{parent_sha}"
            compare_response = requests.get(compare_url)
            if compare_response.status_code == 200:
                compare_data = compare_response.json()
                # If the commit is part of the branch, return the commit's date
                if (
                    compare_data["status"] == "behind"
                    or compare_data["status"] == "identical"
                ):
                    return get_commit_by_sha(
                        commit_sha=parent_sha, owner=owner, repo=repo
                    )
    elif response.status_code == 404:
        return None
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    return None


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
