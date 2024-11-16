import inspect
from urllib3.exceptions import ProtocolError
from http.client import RemoteDisconnected
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from selenium.common.exceptions import JavascriptException
from chatgpt_auto.chat_utils import printf, remove_stacktrace
from chatgpt_auto.constants import *
from chatgpt_auto import ChatGPTAuto
import os


def main() -> None:
    chatgpt_auto = ChatGPTAuto(cleanup=False)

    prompt_history = FileHistory(Paths.PROMPT_HISTORY)
    session = PromptSession(history=prompt_history)

    is_stderror = False
    user_prompt = ""
    os.system("clear")
    while True:
        try:
            if not is_stderror:
                user_prompt = session.prompt("\n>>> ")
                if user_prompt.startswith("code"):
                    user_prompt = user_prompt.replace("code", "") + Variables.PROMPT_FORMULA

            chat_response = chatgpt_auto.send(user_prompt)
            if isinstance(chat_response, str): 
                print(f"ChatGPT said: {chat_response}")
                continue
            # cmd_output, is_stderror = chatgpt_auto.handle_code(chat_response)

            # user_prompt = cmd_output

        except (
            JavascriptException,
            AssertionError,
            AttributeError,
            IOError,
            KeyError,
            TimeoutError
        ) as e:
            printf(remove_stacktrace(e))

        except (ProtocolError, RemoteDisconnected):
            print("Remote end closed connection without response. Reinitializing ChatGPTAuto...")
            chatgpt_auto = ChatGPTAuto(cleanup=False)

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
