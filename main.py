import inspect
from time import sleep
from selenium.common.exceptions import JavascriptException
from chat_utils import printf
from constants import *
from helper import Helper


def main() -> None:
    helper = Helper()
    helper.load_chatgpt_with_cookies()
    helper.clean_up_page()
    is_run = True

    prompt = HEADER + " " + input("\n-> You: ")

    while is_run:
        try:
            codes: list[tuple[str, str]] = helper.send_prompt(prompt)

            is_run = codes is None or len(codes) == 0
            
            logs: str = helper.handle_codes(codes)
            steps = logs.strip().split("\n")
            for step in steps:
                printf(f"Step {steps.index(step)+1}/{len(steps)}:\n{step}")

            prompt = logs.replace("\n", "")

            is_run = len(prompt) == 0

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
            printf(f"Error occurred at {inspect.stack()[1].function}: {e_formatted}")
            
            sleep(1)



if __name__ == "__main__":
    main()
