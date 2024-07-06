from typing import List
import requests

from chat_with_repo.commit_tools import is_commit_in_branch


def find_branches_by_commit(
    commit_sha: str, owner: str = "smeup", repo: str = "jariko"
) -> List[str]:
    branches_by_commit = []

    # List all branches
    branches_url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    branches_response = requests.get(branches_url)
    branches = branches_response.json()

    for branch in branches:
        branch_name = branch["name"]
        if is_commit_in_branch(
            commit_sha=commit_sha, branch=branch_name, owner=owner, repo=repo
        ):
            branches_by_commit.append(branch_name)

    return branches_by_commit
