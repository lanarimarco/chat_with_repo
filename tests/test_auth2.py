from chat_with_repo import CLIENT_SECRET, REDIRECT_URI
from chat_with_repo.auth2 import __create_flow


def test_requirements():
    assert CLIENT_SECRET["web"] is not None
    assert REDIRECT_URI is not None
