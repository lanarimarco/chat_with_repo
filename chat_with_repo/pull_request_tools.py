from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool


from typing import Callable, List, Tuple, Type

from pydantic import BaseModel
import requests

from chat_with_repo import GITHUB_TOKEN
from chat_with_repo.assistant.commit_tools import get_commits_by_path
from chat_with_repo.model import PullRequest, PullRequestState, PullRequestFilter


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


def get_pull_requests_by_commit(
    commit_sha: str, owner: str = "smeup", repo: str = "jariko"
) -> List[PullRequest]:
    """
    Retrieves the pull requests associated with a given commit SHA.

    Args:
        commit_sha (str): The SHA of the commit.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        List[PullRequest]: A list of PullRequest objects representing the retrieved pull requests.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/pulls"
    headers = {
        "Accept": "application/vnd.github.groot-preview+json",  # Required for this API
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [PullRequest.model_validate(pr) for pr in response.json()]
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


def get_pull_requests(
    pull_request_filter: PullRequestFilter = PullRequestFilter(),
    owner: str = "smeup",
    repo: str = "jariko",
    direction: str = "desc",
) -> List[PullRequest]:
    """
    Retrieves a list of pull requests based on the provided filter criteria.

    Args:
        pull_request_filter (PullRequestFilter, optional): The filter criteria for the pull requests. Defaults to an empty filter.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".
        direction (str, optional): The direction of the pull requests searched in github (asc|desc). Defaults to "desc"

    Returns:
        List[PullRequest]: A list of pull requests that match the filter criteria, In case the filter provide title or body, the pull requests are sorted by the number of matched words descending.
    """
    return __get_pull_requests(
        opened_from_branch=pull_request_filter.opened_from_branch,
        owner=owner,
        repo=repo,
        target_branch=pull_request_filter.target_branch,
        state=pull_request_filter.state,
        direction=direction,
        pull_request_matches_filter=lambda pr: __is_pull_request_match_filter(
            pr, pull_request_filter
        ),
    )


def get_pull_requests_by_path(
    path: str, owner: str = "smeup", repo: str = "jariko"
) -> List[PullRequest]:
    """
    Retrieves the pull requests that have modified a given file.

    Args:
        path (str): The path of the file.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".

    Returns:
        List[PullRequest]: A list of PullRequest objects representing the retrieved pull requests.
    """
    commits = get_commits_by_path(path=path, owner=owner, repo=repo)
    pull_requests = []
    for commit in commits:
        pull_requests += [
            pr
            for pr in get_pull_requests_by_commit(commit.sha, owner, repo)
            if pr not in pull_requests
        ]
    return pull_requests


class PullRequestMatched(BaseModel):
    matched: bool = True
    matched_words_count: int = 0


def __is_pull_request_match_filter(
    pull_request: PullRequest, pull_request_filter: PullRequestFilter
) -> PullRequestMatched:
    matched_words_count = 0
    title = __extract_only_useful_information(pull_request.title)
    title_filter = (
        None
        if pull_request_filter.title is None
        else __extract_only_useful_information(pull_request_filter.title)
    )
    body = (
        None
        if pull_request.body is None
        else __extract_only_useful_information(pull_request.body)
    )
    body_filter = (
        None
        if pull_request_filter.body is None
        else __extract_only_useful_information(pull_request_filter.body)
    )
    if (
        pull_request_filter.number is not None
        and pull_request.number != pull_request_filter.number
    ):
        return PullRequestMatched(matched=False)

    if title_filter is not None and not any(
        word.upper() in title.upper() for word in title_filter.split()
    ):
        return PullRequestMatched(matched=False)
    elif title_filter is not None:
        for word in title_filter.split():
            matched_words_count += title.upper().split().count(word.upper())

    if body_filter is not None and (
        body is None
        or not any(word.upper() in body.upper() for word in body_filter.split())
    ):
        return PullRequestMatched(matched=False)
    elif body_filter is not None and body is not None:
        for word in body_filter.split():
            matched_words_count += body.upper().split().count(word.upper())

    return PullRequestMatched(matched_words_count=matched_words_count)


def __get_pull_requests(
    opened_from_branch: str = None,
    owner: str = "smeup",
    repo: str = "jariko",
    target_branch: str = "develop",
    state: PullRequestState = PullRequestState.ALL,
    direction: str = "desc",
    pull_request_matches_filter: Callable[
        [PullRequest], PullRequestMatched
    ] = lambda pr: True,
) -> List[PullRequest]:
    """
    Retrieves a list of pull requests from a GitHub repository.

    Args:
        owner (str): The owner of the repository. Defaults to "smeup".
        repo (str): The name of the repository. Defaults to "jariko".
        target_branch (str): The target branch of the pull requests. Defaults to "develop".
        state (PullRequestState): The state of the pull requests. Defaults to PullRequestState.ALL.
        direction (str): The direction of the pull requests. Defaults to "desc".

    Returns:
        List[PullRequest]: A list of PullRequest objects representing the retrieved pull requests.

    Raises:
        Exception: If there is an error making the API request or processing the response.

    """
    # Make the API request
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    params = {
        "base": f"{target_branch}",
        "direction": f"{direction}",
        "per_page": 100,
    }
    if state:
        params["state"] = state.value
    if opened_from_branch:
        params["head"] = f"{owner}:{opened_from_branch}"

    nextUrl = url
    pull_requests_with_matched_chars: List[Tuple[PullRequest, int]] = []

    while nextUrl:
        print(f"Processing {nextUrl}")
        response = requests.get(nextUrl, headers=headers, params=params)
        # Check if the request was successful
        if response.status_code == 200:
            nextUrl = response.links.get("next", {}).get("url")
            # Process the pull requests as needed
            pr_dict = response.json()
            for pr in pr_dict:
                pull_request = PullRequest.model_validate(pr)
                pull_request_matched = pull_request_matches_filter(pull_request)
                if pull_request_matched.matched:
                    pull_requests_with_matched_chars.append(
                        (pull_request, pull_request_matched.matched_words_count)
                    )

        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    pull_requests_with_matched_chars.sort(key=lambda x: x[1], reverse=True)
    return [pr[0] for pr in pull_requests_with_matched_chars]


def __extract_only_useful_information(text: str) -> str:
    return __remove_duplicated_words(__preserve_only_letters_and_numbers(text))


def __preserve_only_letters_and_numbers(text: str) -> str:
    return "".join([c for c in text if c.isalnum() or c == " "])


def __remove_duplicated_words(text: str) -> str:
    words = text.split()
    unique_words = " ".join(dict.fromkeys(words))
    return unique_words
