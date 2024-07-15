from typing import List, Type
import requests
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from chat_with_repo import GITHUB_TOKEN
from chat_with_repo.commit_tools import is_commit_in_base
from chat_with_repo.model import State


class FindBranchesByCommitSchema(BaseModel):
    commit_sha: str = Field(..., title="The commit SHA to search for.")


class FindBranchesByCommitTool(BaseTool):
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = FindBranchesByCommitSchema
    name: str = "find_branches_by_commit"
    description = "Retrieves the branches that contain a specific commit."

    def _run(self, commit_sha: str) -> List[str]:
        return find_branches_by_commit(
            commit_sha=commit_sha,
            owner=self.state.repo.owner,
            repo=self.state.repo.name,
        )[: self.topK]


def find_branches_by_commit(
    commit_sha: str, owner: str = "smeup", repo: str = "jariko"
) -> List[str]:
    """
    Finds the branches that contain a specific commit.
    args:
        commit_sha: The commit SHA to search for.
        owner: The owner of the GitHub repository. Defaults to "smeup".
        repo: The name of the GitHub repository. Defaults to "jariko".

    returns:
        A list of branch names that contain the specified commit.
    """

    # List all branches
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    params = {
        "per_page": 100,
    }

    nextUrl = url
    branches_by_commit = []
    while nextUrl:
        response = requests.get(url=nextUrl, headers=headers, params=params)
        if response.status_code == 200:
            nextUrl = response.links.get("next", {}).get("url")
            branches = response.json()
            for branch in branches:
                branch_name = branch["name"]
                if is_commit_in_base(
                    commit_sha=commit_sha, base=branch_name, owner=owner, repo=repo
                ):
                    branches_by_commit.append(branch_name)
        else:
            raise Exception(
                f"Error: {response.status_code} - {response.text}",
                f"Check if your profile has the rights for {url}",
            )
    return branches_by_commit
