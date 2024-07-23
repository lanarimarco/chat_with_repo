from typing import List

from chat_with_repo import AUTHORAZED_USERS

from enum import Enum


class User:
    def __init__(self, email: str, name: str, avatar: bytes):
        self.email = email
        self.name = name
        self.avatar = avatar


class Authorization:
    def __init__(self, email: str, authorized: bool = True):
        self.email = email
        self.authorized = authorized


class AuthorizationManager:

    def __init__(self):
        pass

    def is_authorized(self, email: str) -> bool:
        for user in get_authorized_users():
            if user.email.upper() == email.upper():
                return user.authorized
        return False


def get_authorized_users() -> List[Authorization]:
    return [Authorization(email.strip()) for email in AUTHORAZED_USERS.split(",")]
