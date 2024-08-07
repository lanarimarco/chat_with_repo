from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate


from typing import Callable, List, Optional, Tuple, Type

from langchain_openai import ChatOpenAI
import requests
import hashlib

from chat_with_repo import GITHUB_TOKEN, MODEL_NAME, OPENAI_API_KEY
from chat_with_repo.commit_tools import (
    get_commits_by_path,
    get_commits_by_pull_request,
    is_commit_in_base,
)
from chat_with_repo.constants import CODE_REVIEW_SYSTEM_MESSAGE, CODE_REVIEW_TEMPLATE
from chat_with_repo.model import (
    Commit,
    FileChange,
    PullRequest,
    PullRequestState,
    PullRequestFilter,
    State,
)


class GetPullRequestByNumberSchema(BaseModel):
    number: int = Field(..., description="The number of the pull request.")


class GetPullRequestByNumberTool(BaseTool):
    state: State
    args_schema: Type[BaseModel] = GetPullRequestByNumberSchema
    name: str = "get_pull_request_by_number"
    description = "Retrieves a pull request by its number."

    def _run(self, number: int) -> Optional[PullRequest]:
        return get_pull_request_by_number(
            number=number, owner=self.state.repo.owner, repo=self.state.repo.value
        )


class GetPullRequestsByCommitShema(BaseModel):
    commit_sha: str = Field(..., description="The SHA of the commit.")


class GetPullRequestsByCommitTool(BaseTool):
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = GetPullRequestsByCommitShema
    name: str = "get_pull_requests_by_commit"
    description = "Retrieves a list of pull requests associated with a specific commit."

    def _run(self, commit_sha: str) -> List[PullRequest]:
        return get_pull_requests_by_commit(
            commit_sha=commit_sha,
            owner=self.state.repo.owner,
            repo=self.state.repo.value,
        )[: self.topK]


class GetPullRequestByPathSchema(BaseModel):
    path: str = Field(..., description="The path to the file.")


class GetPullRequestByPathTool(BaseTool):
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = GetPullRequestByPathSchema
    name: str = "get_pull_requests_by_path"
    description = "Retrieves a list of pull requests associated with a specific file."

    def _run(self, path: str) -> List[PullRequest]:
        return get_pull_requests_by_path(
            path=path, owner=self.state.repo.owner, repo=self.state.repo.value
        )[: self.topK]


class GetPullRequestsByCommitShema(BaseModel):
    commit_sha: str = Field(..., description="The SHA of the commit.")


class GetPullRequestsByCommitTool(BaseTool):
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = GetPullRequestsByCommitShema
    name: str = "get_pull_requests_by_commit"
    description = "Retrieves a list of pull requests associated with a specific commit."

    def _run(self, commit_sha: str) -> List[PullRequest]:
        return get_pull_requests_by_commit(
            commit_sha=commit_sha,
            owner=self.state.repo.owner,
            repo=self.state.repo.value,
        )[: self.topK]


class GetPullRequestsSchema(BaseModel):
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
    state: State
    topK: int = 10
    args_schema: Type[BaseModel] = GetPullRequestsSchema
    name: str = "get_pull_requests"
    description = "Retrieves a list of pull requests based on the provided filters."

    def _run(
        self,
        title: str = None,
        body: str = None,
        opened_from_branch: str = None,
        target_branch: str = "develop",
        state: PullRequestState = PullRequestState.ALL,
    ) -> List[PullRequest]:
        return get_pull_requests(
            PullRequestFilter(
                title=title,
                body=body,
                opened_from_branch=opened_from_branch,
                target_branch=target_branch,
                state=state,
            ),
            owner=self.state.repo.owner,
            repo=self.state.repo.value,
        )[: self.topK]


class CodeReviewSchema(BaseModel):
    number: int = Field(..., description="The pull request number.")


class PromptProperty:
    def __init__(
        self,
        description: str,
        diff: str,
        commits: List[Commit],
        links_diff: dict[str, str],
        excluded_links_diff: dict[str, str],
    ):
        self.diff = diff
        self.description = description
        self.diff = diff
        self.commits = commits
        self.links_diff = links_diff
        self.excluded_links_diff = excluded_links_diff


class CodeReviewTool(BaseTool):
    args_schema: Type[BaseModel] = CodeReviewSchema
    state: State
    name: str = "code_review"
    description = "Makes a code review of the pull request"
    return_direct = True

    def _run(self, number: int) -> str:

        llm = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_messages(
            [("system", CODE_REVIEW_SYSTEM_MESSAGE), ("user", CODE_REVIEW_TEMPLATE)]
        )
        chain = prompt | llm
        prompt_property = create_prompt_property(
            number=number, owner=self.state.repo.owner, repo=self.state.repo.value
        )
        return chain.invoke(
            {
                "input": self.state.messages[-1].content,
                "description": prompt_property.description,
                "diff": prompt_property.diff,
                "commits": prompt_property.commits,
                "links_diff": prompt_property.links_diff,
                "excluded_links_diff": prompt_property.excluded_links_diff,
            }
        ).content


# This tool is into this module to avoid circular imports
class IsCommitInBranchSchema(BaseModel):
    commit_sha: str = Field(..., description="The commit SHA.")
    branch: str = Field(..., description="The branch name.")


class IsCommitInBranchTool(BaseTool):
    state: State
    args_schema: Type[BaseModel] = IsCommitInBranchSchema
    name: str = "is_commit_in_branch"
    description = "Verifies if a commit is in a branch."

    def _run(self, commit_sha: str, branch: str) -> bool:
        pull_requests_by_commit = get_pull_requests_by_commit(
            commit_sha=commit_sha,
            owner=self.state.repo.owner,
            repo=self.state.repo.value,
        )
        if len(pull_requests_by_commit) > 0:
            return True
        return is_commit_in_base(
            commit_sha=commit_sha,
            base=branch,
            owner=self.state.repo.owner,
            repo=self.state.repo.value,
        )


##########################################################################


def get_pull_request_by_number(
    number: int, owner: str = "smeup", repo: str = "jariko"
) -> Optional[PullRequest]:
    """
    Retrieves a pull request by its number.
        number (int): The number of the pull request.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "webup-project".
    Returns:
        Optional[PullRequest]: The pull request with the given number, or None if it does not exist.
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return PullRequest.model_validate(response.json())
    elif response.status_code == 404:
        return None
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


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
    params = {
        "per_page": 100,
    }

    nextUrl = url
    pull_requests = []
    while nextUrl:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            nextUrl = response.links.get("next", {}).get("url")
            pull_requests += [PullRequest.model_validate(pr) for pr in response.json()]
        elif response.status_code == 422 or response.status_code == 404:
            return []
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    return pull_requests


def get_diff(number: int, owner: str = "smeup", repo: str = "jariko") -> str:
    """Retrieves the diff content of a pull request.

    Args:
        number (int): The number of the pull request.
        owner (str, optional): The owner of the repo. Defaults to "smeup".
        repo (str, optional): The name of the repo. Defaults to "jariko".

    Returns:
        str: The diff content of the pull request.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(url=api_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


def exclude_files_from_diff(diff: str, remove_file_with_paths: List[str]) -> str:
    """
    Removes the specified files from the diff content.

    Args:
        diff (str): The diff content.
        remove_file_with_paths (List[str]): The paths of the files to remove.

    Returns:
        str: The diff content with the specified files removed.
    """
    diff_lines = diff.splitlines()
    filtered_diff = []
    skip = False
    for line in diff_lines:
        if line.startswith("diff --git"):
            skip = any(path in line for path in remove_file_with_paths)
        if not skip:
            filtered_diff.append(line)
    return "\n".join(filtered_diff)


def generate_diff_hash(file_path: str) -> str:
    """
    Generates a diff hash for a given file path.

    Args:
        file_path (str): The path of the file within the repository.

    Returns:
        str: The generated diff hash.
    """
    sha = hashlib.sha256()
    sha.update(file_path.encode("utf-8"))
    return sha.hexdigest()


def generate_github_diff_url_in_pull_request(
    number: int, file_path: str, owner: str = "smeup", repo: str = "jariko"
) -> str:
    """
    Generates a GitHub diff URL for a specific file in a pull request.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        number (int): The number of the pull request.
        file_path (str): The path of the file within the repository.

    Returns:
        str: The generated GitHub diff URL.
    """
    base_url = f"https://github.com/{owner}/{repo}/pull/{number}/files"
    diff_hash = generate_diff_hash(file_path)
    return f"{base_url}#diff-{diff_hash}"


def get_files_changed_in_pull_request(
    number: int,
    owner: str = "smeup",
    repo: str = "jariko",
    filter: Callable[[FileChange], bool] = lambda file_change: True,
) -> List[FileChange]:
    """
    Retrieves the list of files changed in a given pull request.

    Args:
        number (int): The number of the pull request.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".
        filter (Callable[[FileChange], bool], optional): A function to filter the file changes. Defaults to lambda file_change: True means no filter.

    Returns:
        List[FileChange]: A list of FileChange objects representing the files changed in the pull request.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    params = {
        "per_page": 100,
    }

    nextUrl = url
    files_changed = []
    response = requests.get(url, headers=headers, params=params)
    while nextUrl:
        if response.status_code == 200:
            nextUrl = response.links.get("next", {}).get("url")
            for file in response.json():
                current_file = FileChange.model_validate(file)
                if filter(current_file):
                    files_changed.append(current_file)
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    return files_changed


def create_prompt_property(number: int, owner="smeup", repo="jariko") -> PromptProperty:
    """
    Creates a PromptProperty object with the information of the pull request.
        number (int): The number of the pull request.
        owner (str, optional): The owner of the repository. Defaults to "smeup".
        repo (str, optional): The name of the repository. Defaults to "jariko".
    Returns: PromptProperty: The PromptProperty object with the information of the pull request.
    """
    pull_request = get_pull_request_by_number(number=number, owner=owner, repo=repo)

    title: str = pull_request.title
    body: str = "" if pull_request.body is None else pull_request.body

    description: str = f"""
    Title: {title} 
    Body: {body}
"""

    excluded_file_names: List[str] = []

    def filter_file_change(file_change: FileChange) -> bool:
        if file_change.changes <= 500:
            return True
        else:
            excluded_file_names.append(file_change.filename)
            return False

    files_changed_in_pull_request: List[FileChange] = get_files_changed_in_pull_request(
        number=number, owner=owner, repo=repo, filter=filter_file_change
    )

    commits: List[Commit] = get_commits_by_pull_request(
        number=number, owner=owner, repo=repo
    )

    diff: str = get_diff(number=number, owner=owner, repo=repo)

    diff = exclude_files_from_diff(diff, excluded_file_names)

    links_diff: dict[str, str] = {}
    for file in files_changed_in_pull_request:
        links_diff[file.filename] = generate_github_diff_url_in_pull_request(
            number=number,
            file_path=file.filename,
            owner=owner,
            repo=repo,
        )

    excluded_links_diff: dict[str, str] = {}
    for file in excluded_file_names:
        excluded_links_diff[file] = generate_github_diff_url_in_pull_request(
            number=number,
            file_path=file,
            owner=owner,
            repo=repo,
        )
    return PromptProperty(
        diff=diff,
        description=description,
        commits=commits,
        links_diff=links_diff,
        excluded_links_diff=excluded_links_diff,
    )


def __extract_only_useful_information(text: str) -> str:
    return __remove_duplicated_words(__preserve_only_letters_and_numbers(text))


def __preserve_only_letters_and_numbers(text: str) -> str:
    return "".join([c for c in text if c.isalnum() or c == " "])


def __remove_duplicated_words(text: str) -> str:
    words = text.split()
    unique_words = " ".join(dict.fromkeys(words))
    return unique_words
