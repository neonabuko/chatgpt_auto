import inspect
from selenium.common.exceptions import JavascriptException
from chat_utils import printf
from constants import *
from helper import Helper
import os


def main() -> None:
    helper = Helper(is_do_cleanup=False)
    is_run = True
    prompt = PROMPT_HEADER + " " + input("\n-> You: ")

    os.system('clear')
    while is_run:
        try:
            response = helper.send_prompt(prompt)
            
            output = helper.handle_code(response)

            print(output)

            prompt = output

        except JavascriptException as j:
            jf = helper.remove_stacktrace(j)
            printf(jf)

        except KeyboardInterrupt:
            printf("\nKeyboard Interrupt")
            is_run = False

        except Exception as e:
            ef = helper.remove_stacktrace(e)
            printf(ef)
            printf(f"Exception: {inspect.stack()[1].function}: {ef}")


if __name__ == "__main__":
    main()
