import inspect
import queue
from time import sleep
from selenium.common.exceptions import JavascriptException
from chat_utils import printf
from constants import *
from helper import Helper


def main() -> None:
    helper = Helper()
    helper.load_chatgpt_with_cookies()
    is_run = True
    is_has_errors = False
    send_prompt_with_errors = False
    prompt = ""

    messages_queue = queue.Queue()
    helper.start_content_watch(messages_queue)
    while is_run:
        try:
            if not send_prompt_with_errors:
                prompt = PROMPT_HEADER + " " + input("\n-> You: ")

            response: list[tuple[str, str]] | str = helper.send_prompt(prompt)
            response = response or []
            
            if isinstance(response, list):
                logs, is_has_errors = helper.handle_codes(response)

                if is_has_errors:
                    send_prompt_with_errors = str(input("Send errors for analysis? [y/n]: ")) == 'y'
                else:
                    send_prompt_with_errors = False

                prompt = logs.replace("\n", "")
            elif isinstance(response, str):
                printf(response, prefix="\n")

        except JavascriptException as j:
            j_formatted = helper.remove_stacktrace(j)
            printf(j_formatted)
            sleep(1)

        except KeyboardInterrupt:
            printf("\nKeyboard Interrupt")
            is_run = False

        except Exception as e:
            e_formatted = helper.remove_stacktrace(e)
            printf(e_formatted)
            printf(f"Exception occurred at {inspect.stack()[1].function}: {e_formatted}")
            sleep(1)


if __name__ == "__main__":
    main()
