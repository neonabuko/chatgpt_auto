import inspect

class ChatGPTAutoException(Exception):
    def __init__(self, message="") -> None:
        func_name = inspect.stack()[1].function
        super().__init__(f"{func_name}() -> {message}")