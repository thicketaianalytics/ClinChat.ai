from typing import TypedDict


class User(TypedDict):
    email: str
    password_hash: str