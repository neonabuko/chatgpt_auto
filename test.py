import multiprocessing
from multiprocessing.connection import Listener
from time import sleep
from selenium.common.exceptions import JavascriptException
from constants import CHAT, CHAT_2
from custom_exceptions import HelperException
from helper import Helper
from test_constants import *
from manager import Manager


manager = Manager()


def main():
    chat_1 = Helper(CHAT, None)
    chat_2 = Helper(CHAT_2, None)
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

            elif command.startswith("start_conversation"):
                if manager.stop.is_set():
                    manager.stop.clear()

                initial_prompt = command.replace("start_conversation ", "", 1)
                talk_thread = start_conversation_process(
                    chat_1, chat_2, initial_prompt
                )
                conn.send("Started conversation")
                manager.color_print(f"Prompt: {initial_prompt}\n", YELLOW)

            elif command == "stop_conversation":
                if talk_thread is not None:
                    manager.stop.set()
                    while not manager.queue.empty():
                        manager.queue.get()
                    conn.send("Stopped conversation.")
                else:
                    conn.send("No ongoing conversation.")
            else:
                conn.send(
                    "Unrecognized command. Try one of these:\nquit\nis_alive\nstart_conversation\nstop_conversation"
                )

            conn.close()
        except KeyboardInterrupt:
            manager.stop.set()
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


def start_conversation(chat_1: Helper, chat_2: Helper, initial_prompt: str) -> None:
    current_chat = chat_1
    while not manager.stop.is_set():
        try:
            response = current_chat.send_prompt(initial_prompt)
            manager.queue.put(response)

            initial_prompt = response
            if current_chat == chat_1:
                current_chat = chat_2
            else:
                current_chat = chat_1
        except:
            continue


def read_responses():
    color = BLUE
    first = 2
    while not manager.stop.is_set():
        try:
            response = manager.queue.get(timeout=1)
        except:
            continue
        if response is not None:
            if isinstance(response, list):
                response = response[0]
            f_response = manager.filter_response(response)
            sentences = manager.break_down(f_response)
            pitch_change = first
            manager.start_gen_tts(sentences, pitch_change)
            manager.color_print(f"{f_response}\n", color)

            while manager.is_reading_aloud:
                sleep(.3)
                pass
            manager.is_reading_aloud = True
            manager.read_aloud(1.8)
            manager.is_reading_aloud = False

            color = GREEN if color == BLUE else BLUE
            first = 2 if first == -2 else -2


def start_conversation_process(
    chat_1: Helper, chat_2: Helper, initial_prompt: str
):
    conversation = multiprocessing.Process(
        target=start_conversation,
        args=(
            chat_1,
            chat_2,
            initial_prompt,
        ),
    )
    conversation.daemon = True
    conversation.start()

    reading = multiprocessing.Process(target=read_responses)
    reading.start()

    return conversation


if __name__ == "__main__":
    main()
