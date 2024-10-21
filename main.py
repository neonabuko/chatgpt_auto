import inspect
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

    while is_run:
        try:
            helper.clean_up_page()
            if not send_prompt_with_errors:
                prompt = PROMPT_HEADER + " " + input("\n-> You: ")

            codes: list[tuple[str, str]] = helper.send_prompt(prompt)
            codes = codes or []
            
            logs, is_has_errors = helper.handle_codes(codes)

            if is_has_errors:
                send_prompt_with_errors = str(input("Send errors for analysis? [y/n]: ")) == 'y'
            else:
                send_prompt_with_errors = False

            prompt = logs.replace("\n", "")

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
