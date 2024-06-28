from typing import List
from chat_with_repo.commit_tools import __get_commits, get_commits_by_path
from chat_with_repo.pull_request_tools import (
    get_pull_requests,
    get_pull_requests_by_commit,
    get_pull_requests_by_path,
)
from chat_with_repo.model import CommitFilter, PullRequest, PullRequestFilter

from chat_with_repo.commit_tools import (
    is_commit_in_branch,
)


def test_get_pull_requests_against_develop():
    # Test case 1: Verify that pull requests are returned correctly
    owner = "smeup"
    repo = "jariko"
    target_branch = "develop"
    direction = "desc"

    pull_requests: List[PullRequest] = get_pull_requests(
        PullRequestFilter(target_branch=target_branch),
        owner=owner,
        repo=repo,
        direction=direction,
    )
    assert len(pull_requests) > 0


def test_get_pull_requests_by_commit():
    # Test case 1: Verify that the correct pull request is returned for a given commit SHA
    commit_sha = "5bc1da09bab1d53b28fbcfdcf9f01fd766bb3b05"
    owner = "smeup"
    repo = "jariko"

    pull_requests: List[PullRequest] = get_pull_requests_by_commit(
        commit_sha=commit_sha, owner=owner, repo=repo
    )

    assert len(pull_requests) == 1
    assert pull_requests[0].number == 534


def test_get_pull_requests_opened_from_branch():
    # Test case 1: perf/chain_with_cache branch
    opened_from_branch = "perf/chain_with_cache"
    owner = "smeup"
    repo = "jariko"
    pull_request_filter = PullRequestFilter(
        opened_from_branch=opened_from_branch, target_branch="develop"
    )
    pull_requests: List[PullRequest] = get_pull_requests(
        pull_request_filter,
        owner=owner,
        repo=repo,
    )

    assert len(pull_requests) == 1
    assert pull_requests[0].number == 535

    # Test case2: perf/chain_with_cache branch
    opened_from_branch = "perf/avoid-logging-reconfiguration"
    owner = "smeup"
    repo = "jariko"
    pull_request_filter = PullRequestFilter(
        opened_from_branch=opened_from_branch, target_branch="develop"
    )
    pull_requests: List[PullRequest] = get_pull_requests(
        pull_request_filter,
        owner=owner,
        repo=repo,
    )

    assert len(pull_requests) == 1
    assert pull_requests[0].number == 534


def test_get_pull_requests_by_title():
    owner = "smeup"
    repo = "jariko"
    pull_request_filter = PullRequestFilter(title="ls24002807")
    pull_requests: List[PullRequest] = get_pull_requests(
        pull_request_filter,
        owner=owner,
        repo=repo,
    )

    assert len(pull_requests) == 1
    assert pull_requests[0].number == 528

    pull_request_filter = PullRequestFilter(title="ls24002988")
    pull_requests: List[PullRequest] = get_pull_requests(
        pull_request_filter,
        owner=owner,
        repo=repo,
    )

    assert len(pull_requests) == 1
    assert pull_requests[0].number == 549


def test_get_pull_requests_by_title_find_none():
    owner = "smeup"
    repo = "jariko"
    pull_request_filter = PullRequestFilter(title="AAAAAAAAAA")
    pull_requests: List[PullRequest] = get_pull_requests(
        pull_request_filter,
        owner=owner,
        repo=repo,
    )
    assert len(pull_requests) == 0


def test_get_pull_requests_by_body_find():
    owner = "smeup"
    repo = "jariko"
    # statement and LS24002807 must be in the body of the pull request
    pull_request_filter = PullRequestFilter(body="statement LS24002807")
    pull_requests: List[PullRequest] = get_pull_requests(
        pull_request_filter,
        owner=owner,
        repo=repo,
    )
    assert len(pull_requests) > 1
    assert pull_requests[0].number == 528


def test_get_pull_requests_by_path():
    # Test case 1: Verify that the correct pull requests are returned for a given file
    path = "rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/execution/Configuration.kt"
    owner = "smeup"
    repo = "jariko"

    pull_requests: List[PullRequest] = get_pull_requests_by_path(
        path=path, owner=owner, repo=repo
    )

    for pr in pull_requests:
        if pr.title == "Feature/errors check improvements":
            assert True
            break
    else:
        assert False


def test_get_not_merged_pull_request():
    owner = "smeup"
    repo = "jariko"
    pull_requests: List[PullRequest] = get_pull_requests(
        PullRequestFilter(merged=False, closed=False),
        owner=owner,
        repo=repo,
    )

    assert len(pull_requests) > 0


def test_get_closed_but_not_merged_pull_request():
    owner = "smeup"
    repo = "jariko"
    pull_requests: List[PullRequest] = get_pull_requests(
        PullRequestFilter(merged=False, closed=True), owner=owner, repo=repo
    )

    assert len(pull_requests) >= 13


def test_get_commits_by_path():
    # Test case 1: Verify that the correct pull requests are returned for a given file
    path = "rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/execution/Configuration.kt"
    owner = "smeup"
    repo = "jariko"

    commits = get_commits_by_path(path=path, owner=owner, repo=repo)

    assert len(commits) > 0


def test_is_commit_in_branch():
    # Test case 1: Verify that the commit is in the branch
    commit_sha = "7d743cdad588a17f2ccad03c190b372554c4bbb5"
    branch = "develop"
    owner = "smeup"
    repo = "jariko"

    assert is_commit_in_branch(commit_sha, branch, owner, repo)
