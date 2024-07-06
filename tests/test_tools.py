from typing import List
from chat_with_repo.commit_tools import (
    compare_commits,
    get_commits_by_path,
    get_commits_by_pull_request,
    is_commit_in_branch,
)
from chat_with_repo.pull_request_tools import (
    get_pull_request_by_number,
    get_pull_requests,
    get_pull_requests_by_commit,
    get_pull_requests_by_path,
)
from chat_with_repo.model import Commit, CommitFilter, PullRequest, PullRequestFilter


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


def test_get_pull_requests_by_number():
    owner = "smeup"
    repo = "webup-project"
    pull_request = get_pull_request_by_number(number=7327, owner=owner, repo=repo)

    assert pull_request.number == 7327


def test_get_pull_requests_by_number_none():
    owner = "smeup"
    repo = "webup-project"
    pull_request = get_pull_request_by_number(number=0, owner=owner, repo=repo)

    assert pull_request is None


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


def test_get_pull_requests_by_commit():
    # Test case 1: Verify that the correct pull request is returned for a given commit SHA
    commit_sha = "58fd35f96f1eb9f087d9613de1cb37b96b2d2e7f"
    owner = "smeup"
    repo = "jariko"

    pull_requests: List[PullRequest] = get_pull_requests_by_commit(
        commit_sha=commit_sha, owner=owner, repo=repo
    )

    assert len(pull_requests) == 1
    assert pull_requests[0].number == 4

    # Test case 2: Verify that if I pass a commit SHA that is not in any pull request, an empty list is returned
    commit_sha = "a16d6cd1dd3b95d7717ac48af18e65e56235ba08"

    pull_requests: List[PullRequest] = get_pull_requests_by_commit(
        commit_sha=commit_sha, owner=owner, repo=repo
    )

    assert len(pull_requests) == 0


def test_get_commits_by_path():
    # Test case 1: Verify that the correct pull requests are returned for a given file
    path = "rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/execution/Configuration.kt"
    owner = "smeup"
    repo = "jariko"

    commits = get_commits_by_path(path=path, owner=owner, repo=repo)

    assert len(commits) > 0


def test_get_commits_by_pull_request():
    # Test case 1: Verify that the commits are returned correctly
    number = 554
    owner = "smeup"
    repo = "jariko"

    commits = get_commits_by_pull_request(number, owner, repo)
    assert any(
        commit.sha == "9474e3ff4f600c9511b14c32e6a6b305350fe0dc" for commit in commits
    )


def test_compare_commits():
    # Test case 1: Verify that the commits are returned correctly
    owner = "smeup"
    repo = "jariko"
    base = "214fe647824ebf369d9b99f5fcebdd84cd6c9b8a"
    head = "ed090f8f507b462165c608cad15c4852bcd9b9f2"

    commits: List[Commit] = compare_commits(
        base=base, head=head, owner=owner, repo=repo
    )

    assert len(commits) == 1
    assert commits[0].sha == "ed090f8f507b462165c608cad15c4852bcd9b9f2"
    assert commits[0].commit.author.email == "davide.palladino@apuliasoft.com"

    # Test case 2: If base or head are not valid commit SHAs, an empty list is returned
    base = "foo"
    head = "ed090f8f507b462165c608cad15c4852bcd9b9f2"

    commits: List[Commit] = compare_commits(
        base=base, head=head, owner=owner, repo=repo
    )

    assert len(commits) == 0


def test_is_commit_in_branch():
    # Test case 1: Verify that the commit is in the develop branch
    owner = "smeup"
    repo = "jariko"
    commit_sha = "cf4dd0747e305d67071587ee25a06e14551f2f76"

    # Test case 1: Verify that the commit is in the develop branch
    branch = "develop"

    assert is_commit_in_branch(
        commit_sha=commit_sha, branch=branch, owner=owner, repo=repo
    )

    # Test case 1: Verify that the commit is in the master branch
    branch = "master"

    assert is_commit_in_branch(
        commit_sha=commit_sha, branch=branch, owner=owner, repo=repo
    )
