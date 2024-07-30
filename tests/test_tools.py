from typing import List
from chat_with_repo.branch_tools import find_branches_by_commit
from chat_with_repo.commit_tools import (
    compare_commits,
    get_commit_by_sha,
    get_commits_by_path,
    get_commits_by_pull_request,
    get_merging_commit,
    is_commit_in_base,
)
from chat_with_repo.pull_request_tools import (
    create_prompt_property,
    generate_github_diff_url_in_pull_request,
    get_diff,
    get_files_changed_in_pull_request,
    get_pull_request_by_number,
    get_pull_requests,
    get_pull_requests_by_commit,
    get_pull_requests_by_path,
    exclude_files_from_diff,
)
from chat_with_repo.model import Commit, CommitFilter, PullRequest, PullRequestFilter
from chat_with_repo.tag_tools import find_tags_by_commit


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

    # Test case 2: Issue https://github.com/lanarimarco/chat_with_repo/issues/4
    commit_sha = "d0b158733fd4d4625bab3c4c854e49b67a89f422"
    pull_requests: List[PullRequest] = get_pull_requests_by_commit(
        commit_sha=commit_sha, owner=owner, repo="kokos-sdk-java-rpgle"
    )
    assert len(pull_requests) == 1


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


def test_get_commits_by_pull_request_filter_all():
    # Test case 1: Verify that the commits are returned correctly
    owner = "smeup"
    repo = "jariko"
    number = 554
    commits = get_commits_by_pull_request(
        number=number, owner=owner, repo=repo, filter=lambda commit: False
    )
    assert len(commits) == 0


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

    # Test case 2: If base or head are not valid commit SHAs, a None is returned
    base = "foo"
    head = "ed090f8f507b462165c608cad15c4852bcd9b9f2"

    commits: List[Commit] = compare_commits(
        base=base, head=head, owner=owner, repo=repo
    )

    assert commits is None


def test_is_commit_in_branch():
    # Test case 1: Verify that the commit is in the develop branch
    owner = "smeup"
    repo = "jariko"
    commit_sha = "cf4dd0747e305d67071587ee25a06e14551f2f76"

    # Test case 1: Verify that the commit is in the develop branch
    base = "develop"
    assert is_commit_in_base(commit_sha=commit_sha, base=base, owner=owner, repo=repo)

    # Test case 2: Verify that the commit is in the master branch
    base = "master"
    assert is_commit_in_base(commit_sha=commit_sha, base=base, owner=owner, repo=repo)

    # Test case 3: If I specify a foo branch, the function should return False
    base = "foo"
    assert (
        is_commit_in_base(commit_sha=commit_sha, base=base, owner=owner, repo=repo)
        == False
    )

    # Test case 4: The commit must be only in the v1.5.1
    base = "v1.5.1"
    commit_sha = "7d743cdad588a17f2ccad03c190b372554c4bbb5"
    assert is_commit_in_base(commit_sha=commit_sha, base=base, owner=owner, repo=repo)

    # Test case 4: The commit must be only in the v1.5.1
    base = "v1.5.0"
    commit_sha = "7d743cdad588a17f2ccad03c190b372554c4bbb5"
    assert is_commit_in_base(commit_sha=commit_sha, base=base, owner=owner, repo=repo)

    # Test case 4: The commit must be only in the v1.5.1
    base = "v1.4.0"
    commit_sha = "7d743cdad588a17f2ccad03c190b372554c4bbb5"
    assert (
        is_commit_in_base(commit_sha=commit_sha, base=base, owner=owner, repo=repo)
        == False
    )

    # Test case 5: Issue https://github.com/lanarimarco/chat_with_repo/issues/4
    # is_commit_in_base does not provide expected results becasue the branches are in diverged status
    base = "develop"
    commit_sha = "d0b158733fd4d4625bab3c4c854e49b67a89f422"
    assert (
        is_commit_in_base(
            commit_sha=commit_sha, base=base, owner="smeup", repo="kokos-sdk-java-rpgle"
        )
        == False
    )


def test_get_commit_by_sha():
    owner = "smeup"
    repo = "jariko"
    commit_sha = "5615e2956bd986d71225498ed1a571ef861f734f"
    commit = get_commit_by_sha(commit_sha=commit_sha, owner=owner, repo=repo)
    assert commit.commit.author.email == "domenico.mancini@apuliasoft.com"


def test_get_commit_by_sha_not_found():
    owner = "smeup"
    repo = "jariko"
    commit_sha = "foo"
    commit = get_commit_by_sha(commit_sha=commit_sha, owner=owner, repo=repo)
    assert commit is None


def test_merging_commit():
    owner = "smeup"
    repo = "jariko"
    branch = "develop"
    commit_sha = "454177945f2cbd33cf859dc54abd4da92eb3c1a5"
    commit: Commit = get_merging_commit(
        commit_sha=commit_sha, branch=branch, owner=owner, repo=repo
    )
    assert commit.commit.author.email == "40103274+lanarimarco@users.noreply.github.com"


def test_merging_commit_not_found():
    owner = "smeup"
    repo = "jariko"
    branch = "foo"
    commit_sha = "454177945f2cbd33cf859dc54abd4da92eb3c1a5"
    commit: Commit = get_merging_commit(
        commit_sha=commit_sha, branch=branch, owner=owner, repo=repo
    )
    assert commit is None


def test_find_branches_by_commit():
    owner = "smeup"

    repo = "jariko"
    commit_sha = "8d189c51b3ff056aa019c26e93f59e8a603e7735"
    branches = find_branches_by_commit(commit_sha=commit_sha, owner=owner, repo=repo)
    assert "develop" in branches
    assert "master" in branches

    repo = "kokos-sdk-java-rpgle"
    commit_sha = "4a062340c4a4269d1c50c9d553f1f22472209a9d"
    branches = find_branches_by_commit(commit_sha=commit_sha, owner=owner, repo=repo)
    assert "develop" in branches
    assert "master" in branches


def test_find_tags_by_commit():
    owner = "smeup"

    repo = "jariko"
    commit_sha = "c37844f8d7c9246676184c8c883b9251d226f287"
    tags = find_tags_by_commit(commit_sha=commit_sha, owner=owner, repo=repo)
    assert "v1.4.0" in tags

    repo = "webup-project"
    commit_sha = "c5e80832543e92d7ff5c2a2fe941aec4e14af201"
    tags = find_tags_by_commit(
        commit_sha=commit_sha,
        owner=owner,
        repo=repo,
        tag_match_regexp="[0-9]+.[0-9]+.[0-9]+",
    )
    assert "1.20.8" in tags


def test_get_diff_jariko():
    number = 569
    diff = get_diff(number=number)
    assert (
        "diff --git a/rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/execution/Configuration.kt b/rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/execution/Configuration.kt"
        in diff
    )


def test_get_diff_kokos():
    number = 168
    diff = get_diff(number=number, owner="smeup", repo="kokos-sdk-java-rpgle")
    assert (
        "diff --git a/kokos-sdk-rpgle/src/main/java/com/smeup/kokos/sdk/rpgle/syntaxchecker/RpgSyntaxChecker.java"
        in diff
    )


def test_get_diff_webupjs():
    number = 367
    diff = get_diff(number=number, owner="smeup", repo="webup.js")
    assert "cypress/e2e/components/smeup/for/for.cy.ts" in diff
    assert "jest/unit/managers/converters/utilities/dataToJ5.test.ts" in diff


def test_get_files_changed_in_pull_request():
    owner = "smeup"
    repo = "jariko"
    number = 577
    files = get_files_changed_in_pull_request(number=number, owner=owner, repo=repo)
    assert len(files) == 9
    assert (
        files[0].filename
        == "rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/interpreter/compile_time_interpreter.kt"
    )


def test_get_files_changed_in_pull_request_exlude_all():
    owner = "smeup"
    repo = "jariko"
    number = 577
    files = get_files_changed_in_pull_request(
        number=number, owner=owner, repo=repo, filter=lambda x: x.changes < 0
    )
    assert len(files) == 0


def test_generate_github_diff_url_in_pull_request():
    owner = "smeup"
    repo = "jariko"
    number = 577
    file_path = "rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/interpreter/compile_time_interpreter.kt"
    diff_url = generate_github_diff_url_in_pull_request(
        number=number, file_path=file_path, owner=owner, repo=repo
    )
    assert (
        diff_url
        == "https://github.com/smeup/jariko/pull/577/files#diff-f7be7d0ccf3fd32828f9fc29ae1689e278c2f9ce6801212356ac43721946d12c"
    )


def test_exclude_files_from_diff():
    owner = "smeup"
    repo = "jariko"
    diff = get_diff(number=577, owner=owner, repo=repo)
    sanitize_diff = exclude_files_from_diff(
        diff, ["rpgJavaInterpreter-core/src/test/resources/smeup/ERROR29.rpgle"]
    )
    assert (
        "diff --git a/rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/parsing/parsetreetoast/api.kt"
        in sanitize_diff
    )
    assert (
        "+      * Sorgente di origine : SMEUP_DEV/JASRC(D5_091_04)" not in sanitize_diff
    )
    assert (
        "diff --git a/rpgJavaInterpreter-core/src/test/resources/smeup/metadata/D5COSO0F.json"
        in sanitize_diff
    )

def test_create_prompt_property():
    owner = "smeup"
    repo = "jariko"
    number = 577
    prompt_property = create_prompt_property(number=number, owner=owner, repo=repo)
    assert len(prompt_property.commits) == 15
    assert len(prompt_property.excluded_links_diff) == 1
    assert len(prompt_property.links_diff) == 8
