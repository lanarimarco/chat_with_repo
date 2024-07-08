from typing import List, Type
import requests
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from chat_with_repo.commit_tools import is_commit_in_base
from chat_with_repo.model import State


class FindTagsByCommitSchema(BaseModel):
    commit_sha: str = Field(..., title="The commit SHA to search for.")


class FindTagsByCommitTool(BaseTool):
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = FindTagsByCommitSchema
    name: str = "find_tags_by_commit"
    description = "Retrieves the tags that contain a specific commit."

    def _run(self, commit_sha: str) -> List[str]:
        return find_tags_by_commit(
            commit_sha=commit_sha,
            owner=self.state.repo.owner,
            repo=self.state.repo.name,
        )[: self.topK]


def find_tags_by_commit(
    commit_sha: str, owner: str = "smeup", repo: str = "jariko"
) -> List[str]:
    tags_by_commit = []

    # List all tags
    tags_url = f"https://api.github.com/repos/{owner}/{repo}/tags"
    response = requests.get(tags_url)

    if response.status_code == 200:
        tags = response.json()
        for tag in tags:
            tag_name = tag["name"]
            tag_commit_sha = tag["commit"]["sha"]
            # print("checking tag", tag_name, tag_commit_sha)
            if is_commit_in_base(
                commit_sha=commit_sha, base=tag_commit_sha, owner=owner, repo=repo
            ):
                tags_by_commit.append(tag_name)
            else:
                if len(tags_by_commit) > 0:
                    # since tags are ordered by descending, we can break if we already found a tag because
                    # we know we won't find any more tags
                    break
    else:
        raise Exception(
            f"Error: {response.status_code} - {response.text}",
            f"Check if your profile has the the rights for {tags_url}",
        )
    return tags_by_commit
