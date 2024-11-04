from multiprocessing.connection import Listener
from selenium.common.exceptions import JavascriptException, TimeoutException
from constants import CHAT_1, CHAT_2
from custom_exceptions import ChatGPTAutoException
from chatgpt_auto import ChatGPTAuto
from test_constants import *
from chatgpt_yapper import ChatGPTYapper


def main():
    manager = ChatGPTYapper()
    chat_1 = ChatGPTAuto(CHAT_1, cookies=None, instance_name="Chat 1", cleanup_once=True)
    chat_2 = ChatGPTAuto(CHAT_2, cookies=None, instance_name="Chat 2", cleanup_once=True)
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
                talk_thread = manager.start_conversation_process(
                    chat_1, chat_2, initial_prompt
                )
                conn.send("Started conversation")

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

        except ChatGPTAutoException as h:
            conn.send((str(h)[:250]))

        except JavascriptException as j:
            conn.send((str(j)[:250]))

        except TimeoutException as t:
            conn.send(str(t))
        except Exception as e:
            conn.send((str(e)[:250]))

    listener.close()
    chat_1.driver.quit()
    chat_2.driver.quit()


if __name__ == "__main__":
    main()
