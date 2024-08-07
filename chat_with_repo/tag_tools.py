from typing import List, Type
import requests
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from chat_with_repo import GITHUB_TOKEN
from chat_with_repo.commit_tools import is_commit_in_base
from chat_with_repo.model import State
import re


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
    commit_sha: str,
    tag_match_regexp: str = "v[0-9]+.[0-9]+.[0-9]+",
    owner: str = "smeup",
    repo: str = "jariko",
) -> List[str]:

    # List all tags
    url = f"https://api.github.com/repos/{owner}/{repo}/tags"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    params = {
        "per_page": 100,
    }

    nextUrl = url
    tags_by_commit = []
    force_break = False
    while nextUrl and not force_break:
        response = requests.get(url=nextUrl, headers=headers, params=params)
        if response.status_code == 200:
            tags = response.json()
            for tag in tags:
                tag_name = tag["name"]
                if not re.match(tag_match_regexp, tag_name):
                    continue
                tag_commit_sha = tag["commit"]["sha"]
                if is_commit_in_base(
                    commit_sha=commit_sha, base=tag_commit_sha, owner=owner, repo=repo
                ):
                    tags_by_commit.append(tag_name)
                else:
                    if len(tags_by_commit) > 0:
                        # since tags are ordered by descending, we can break if we already found a tag because
                        # we know we won't find any more tags
                        force_break = True
                        break
            nextUrl = response.links.get("next", {}).get("url")
        else:
            raise Exception(
                f"Error: {response.status_code} - {response.text}",
                f"Check if your profile has the rights for {url}",
            )
    return tags_by_commit
