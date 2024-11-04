import traceback


def printf(obj, prefix="", suffix="\n") -> str:
    print(prefix + str(obj) + suffix)


def remove_stacktrace(exception: BaseException) -> str:
    exception_str = str(exception)
    stacktrace_start = "Stacktrace:"

    if stacktrace_start in exception_str:
        return exception_str.split(stacktrace_start, 1)[0]
    else:
        return exception_str + "\n" + traceback.format_exc()