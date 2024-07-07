from typing import List
import requests

from chat_with_repo.commit_tools import is_commit_in_base


def find_tags_by_commit(
    commit_sha: str, owner: str = "smeup", repo: str = "jariko"
) -> List[str]:
    tags_by_commit = []

    # List all tags
    tags_url = f"https://api.github.com/repos/{owner}/{repo}/tags"
    tags_response = requests.get(tags_url)
    tags = tags_response.json()

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

    return tags_by_commit
