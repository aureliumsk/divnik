from typing import Any
from collections.abc import Callable
from flask import abort

class Message:
    def __init__(self, message: str, argc: int = 0) -> None:
        self.message = message
        self.argc = argc
    def __call__(self, *args) -> str:
        assert len(args) == self.argc
        return self.message.format(*args)

messages = {}

def add_messages(*args: tuple[str, Message]):
    for identifier, message in args:
        messages[identifier] = message

def message(identifier: str) -> Message:
    return messages[identifier]

def should_convert[T](value: Any, converter: Callable[[Any], T], identifier: str, *args, code: int = 400) -> T:
    try:
        return converter(value)
    except Exception:
        abort(code, message(identifier)(*args))