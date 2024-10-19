import subprocess
import traceback
from selenium.common.exceptions import JavascriptException
from chat_utils import printf
from constants import *
from helper import Helper


def main() -> None:
    helper = Helper()
    helper.load_chatgpt_with_cookies()
    
    is_stderror = False

    while True:
        try:
            if not is_stderror:
                helper.clean_up_page()
                prompt = "CHATGPT_AUTO "
                prompt += str(input("\n-> You: "))

            commands = helper.send_prompt(prompt)

            for command in commands:
                n_commands = len(commands)
                current = commands.index(command)

                printf(f"-> Command {current+1}/{n_commands}:\n{command}")
                completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                is_stderror = completed_process.stderr != ""
                output = completed_process.stderr if is_stderror else completed_process.stdout

                prompt = f"-> Output: {output}"
                printf(prompt)

                if is_stderror:
                    break

        except JavascriptException as j:
            j = remove_stacktrace(j)
            printf(f"Javascript Exception: {j}")
            is_stderror = False

        except KeyboardInterrupt:
            printf("\nKeyboard Interrupt")
            exit()

        except Exception as e:
            e = remove_stacktrace(e)
            printf(f"Exception: {e}")
            is_stderror = False


def remove_stacktrace(exception: BaseException) -> str:
    exception = str(exception)
    stacktrace_start = "Stacktrace:"
    if stacktrace_start in exception:
        stacktrace = exception[exception.find(stacktrace_start):]
        exception = exception.replace(stacktrace, "")
    else:
        exception += "\n" + traceback.format_exc()

    return exception


if __name__ == '__main__':
    main()
