from chat_with_repo.assistant import GitHubAssistant


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

def test_is_commit_in_branch():
    assistant = GitHubAssistant()
    message = """
        Hello, tell me if the commit 7d743cdad588a17f2ccad03c190b372554c4bbb5 is in the branch develop
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
