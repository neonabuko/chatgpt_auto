import inspect
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from selenium.common.exceptions import JavascriptException
from chat_utils import printf, remove_stacktrace
from constants import *
from chatgpt_auto import ChatGPTAuto
import os


def main() -> None:
    chatgpt_auto = ChatGPTAuto(cleanup=False)

    prompt_history = FileHistory(PROMPT_HISTORY)
    session = PromptSession(history=prompt_history)

    is_stderror = False
    os.system("clear")
    while True:
        try:
            if not is_stderror:
                user_prompt = session.prompt("\n-> ") + PROMPT_FORMULA

            chat_response = chatgpt_auto.send(user_prompt)
            terminal_output, is_stderror = chatgpt_auto.handle_code(chat_response)

            user_prompt = terminal_output

        except (JavascriptException, AssertionError, AttributeError, IOError, KeyError) as e:
            printf(remove_stacktrace(e))

        except KeyboardInterrupt:
            printf("\nKeyboard Interrupt")
            break

        except Exception as e:
            ef = remove_stacktrace(e)
            printf(ef)
            printf(f"Exception: {inspect.stack()[1].function}: {ef}")
            break
    
    print("Gracefully quitting driver...")
    chatgpt_auto.driver.quit()


if __name__ == "__main__":
    main()
