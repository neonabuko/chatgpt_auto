import traceback
from typing import Any
from constants import Color


def color_print(text: str, color: str) -> None:
    """Print text with color

    Parameters
    -
    text : str
    """
    print(f"{color}{text}{Color.RESET}")

def printf(obj: Any, prefix: str = "", suffix: str = "\n") -> None:
    """
    Prints an object with optional prefix and suffix.

    Parameters
    -
    obj : Any 
        The object to be printed
    prefix : str
        A string to prefix the output. Default: empty string.
    suffix : str
        A string to suffix the output. Default: newline character.
    """
    print(prefix + str(obj) + suffix)

def remove_stacktrace(exception: BaseException) -> str:
    """
    Removes the stacktrace from an exception message if present. 

    Parameters
    -
    exception : BaseException
        The exception object to process.

    Returns
    -
    str : The exception message with the stacktrace removed, or the full exception message with the stacktrace appended.
    """
    exception_str = str(exception)
    stacktrace_start = "Stacktrace:"

    if stacktrace_start in exception_str:
        return exception_str.split(stacktrace_start, 1)[0]
    else:
        return exception_str + "\n" + traceback.format_exc()
