from multiprocessing.connection import Listener
import threading
from selenium.common.exceptions import JavascriptException
from constants import CHAT, CHAT_2, COOKIES
from custom_exceptions import HelperException
from helper import Helper
from test_constants import *
from manager import Manager


stop = threading.Event()


def main():
    chat_1 = Helper(CHAT, None)
    chat_2 = Helper(CHAT_2, None)
    manager = Manager()
    talk_thread = None

    listener = Listener(address=("localhost", 6000), authkey=b"secret")
    is_run = True
    while is_run:
        try:
            conn = listener.accept()
            command: str = conn.recv()

            if command == "quit":
                conn.close()
                break

            elif command == "is_alive":
                conn.send(True)

            elif command.startswith("talk"):
                if stop.is_set():
                    stop.clear()

                initial_prompt = command.replace("talk ", "", 1)
                talk_thread = start_talking_thread(
                    chat_1, chat_2, manager, initial_prompt
                )
                conn.send("Started talking")
                manager.color_print(f"Prompt: {initial_prompt}\n", YELLOW)

            elif command == "stop_talking":
                if talk_thread is not None:
                    stop.set()
                    conn.send("Stopped talking")

            conn.close()
        except KeyboardInterrupt:
            is_run = False
        except HelperException as h:
            conn.send((str(h)[:250]))
        except JavascriptException as j:
            conn.send((str(j)[:250]))
        except Exception as e:
            conn.send((str(e)[:250]))

    listener.close()
    chat_1.driver.quit()
    chat_2.driver.quit()


def start_talking(
    chat_1: Helper, chat_2: Helper, manager: Manager, initial_prompt: str
) -> None:
    current_chat = chat_1
    color = BLUE
    while not stop.is_set():
        response = current_chat.send_prompt(initial_prompt)
        sentences = manager.format_response(response)
        print("Generating tts...")
        manager.start_gen_tts(sentences)
        manager.color_print(f"{response.text.strip()}\n", color)
        manager.read_aloud(1.8)

        initial_prompt = response.text
        if current_chat == chat_1:
            current_chat = chat_2
            color = GREEN
        else:
            current_chat = chat_1
            color = BLUE


def start_talking_thread(
    chat_1: Helper, chat_2: Helper, manager: Manager, initial_prompt: str
) -> threading.Thread:
    t = threading.Thread(
        target=start_talking,
        args=(
            chat_1,
            chat_2,
            manager,
            initial_prompt,
        ),
    )
    t.daemon = True
    t.start()
    return t


if __name__ == "__main__":
    main()
