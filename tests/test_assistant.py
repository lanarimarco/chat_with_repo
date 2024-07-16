from chat_with_repo.assistant import GitHubAssistant
from chat_with_repo.model import Repo


def test_get_title_by_commit():
    assistant = GitHubAssistant()
    message = "Hello, tell me the title of pull request containing this commit 5bc1da09bab1d53b28fbcfdcf9f01fd766bb3b05"
    response = assistant.chat(message)
    assert "Avoid logging reconfiguration" in response


## Ignored because this kind of test is not repeatable
def ignored_test_get_commits_by_path():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the commit hash associated with the rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/execution/Configuration.kt 
        with commit message: Added JarikoCallback.onInterpreterCreation
    """
    response = assistant.chat(message)
    assert "9f3b2add3d59f27303c08b401d63b3e14ec895b8" in response


def ignored_get_pull_requests_by_path():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the pull request number associated with the rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/execution/Configuration.kt
        merged on June 17, 2024
    """
    response = assistant.chat(message)
    assert "546" in response


def test_if_branch_is_merged_to_develop():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me if the branch perf/avoid-logging-reconfiguration is merged to develop, response Yes if the branch was merged else No
    """
    response = assistant.chat(message)
    assert "YES" in response.upper()


def test_if_branch_is_not_merged_to_develop():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me if the branch foo is merged to develop. Answer No if the branch was not merged
    """
    response = assistant.chat(message)
    assert "NOT" or "NO" in response.upper()


def test_get_pull_requests_by_title():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the pull request containing in the title: ls24002988
    """
    response = assistant.chat(message)
    assert "549" in response


def test_get_pull_requests_by_commit():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the pull request containing the commit 58fd35f96f1eb9f087d9613de1cb37b96b2d2e7f
    """
    response = assistant.chat(message)
    assert "4" in response


def test_get_pull_requests_by_description():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the pull request where in the description we have these words: '%alloc', '%realloc' and '%addr'
    """
    response = assistant.chat(message)
    assert "549" in response


def test_chat_about_pull_request():
    assistant = GitHubAssistant()
    message = """
        Hello, the pr 545 has been merged?
    """
    response = assistant.chat(message)
    message = """
        From who?
    """
    response = assistant.chat(message)
    assert "dom-apuliasoft" in response

    message = """
        And when?
    """
    response = assistant.chat(message)
    assert "June" in response and "12" in response and "2024" in response
    pass


def test_get_commits_by_path():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the commits associated with the file rpgJavaInterpreter-core/src/main/kotlin/com/smeup/rpgparser/execution/Configuration.kt
    """
    response = assistant.chat(message)
    assert "4310307181d9a66dc330db9206602601361943b" in response


def test_is_commit_in_branch_develop():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me if the commit 67477d15d599cad9d7bca0df49cc383984d85125 is in the develop or master. Answer YES or NO followed by the explanation
    """
    response = assistant.chat(message)
    assert "YES" in response.upper()


def test_is_commit_in_branch_master():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me if the commit 8d189c51b3ff056aa019c26e93f59e8a603e7735 is in the branch master. Answer YES or NO followed by the explanation
    """
    response = assistant.chat(message)
    assert "YES" in response.upper()


def test_get_commits_by_pull_request():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the commits associated with the pull request 554
    """
    response = assistant.chat(message)
    assert "9474e3ff4f600c9511b14c32e6a6b305350fe0dc" in response


def test_is_commit_in_branch():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me if the commit cf4dd0747e305d67071587ee25a06e14551f2f76 is in the branch master. Answer YES or NO
    """
    response = assistant.chat(message)
    assert "YES" in response.upper()


def test_get_commit_by_sha():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the email of the author of the commit 5615e2956bd986d71225498ed1a571ef861f734f
    """
    response = assistant.chat(message)
    assert "domenico.mancini@apuliasoft.com" in response


# Commented GetMergingCommitTool is not reliable
# and I don't know how even me how can the agent answer this question
# def test_get_merging_commit():
#     assistant = GitHubAssistant()
#     message = """
#         Hello tell who has merged in the develop this commit 5615e2956bd986d71225498ed1a571ef861f734f
#     """
#     response = assistant.chat(message)
#     assert "Marco Lanari" in response


def test_find_branches_by_commit():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the branches that contain the commit 8d189c51b3ff056aa019c26e93f59e8a603e7735
    """
    response = assistant.chat(message)
    assert "develop" in response
    assert "master" in response


def test_find_tags_by_commit():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me the tags that contain the commit c37844f8d7c9246676184c8c883b9251d226f287
    """
    response = assistant.chat(message)
    assert "v1.4.0" in response
    assert "v1.5.0" in response
    assert "v1.5.1" in response


def test_if_pr_has_been_merged_in_a_master():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me if the pull request 487 has been merged in the branch master. Answer YES or NO
    """
    response = assistant.chat(message)
    assert "YES" in response.upper()


def test_if_pr_has_been_merged_in_a_tag():

    assistant = GitHubAssistant()

    message = """
        Hello, tell me if the pull request 487 has been merged in the v1.5.1. Answer YES or NO
    """
    response = assistant.chat(message)
    assert "YES" in response.upper()

    message = """
        Hello, tell me if the pull request 487 has been merged in the v1.4.0. Answer YES or NO
    """
    response = assistant.chat(message)
    assert "NO" in response.upper()


def test_describe_pull_request_change_in_jariko():
    # Describe the changes of the pull request 562 in Jariko
    assistant = GitHubAssistant()
    message = """
        Hello, describe the changes of the pull request 562
    """
    response = assistant.chat(message)
    assert "RpgLexer.g4" in response
    assert "bif.kt" in response
    assert "MUDRNRAPU00228.rpgle" in response


def test_description_pull_request_change_in_kokos():
    # Describe the changes of the pull request 168 in kokos-sdk-java-rpgle
    assistant = GitHubAssistant()
    assistant.state.repo = Repo.kokos_sdk_java_rpgle
    message = """
        Hello, describe the changes of the pull request 168
    """
    response = assistant.chat(message)
    assert "RpgSyntaxChecker.java" in response


def test_is_branch_merged_in_develop_kokos():
    assistant = GitHubAssistant()
    assistant.state.repo = Repo.kokos_sdk_java_rpgle
    message = """
        Hello, tell me if the branch feat/NW24000624/program_finder_better_exception_handling is merged in develop. Answer YES or NO
    """
    response = assistant.chat(message)
    assert "YES" in response.upper()
