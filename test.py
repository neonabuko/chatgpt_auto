from multiprocessing.connection import Listener
from selenium.common.exceptions import JavascriptException, TimeoutException
from custom_exceptions import ChatGPTAutoException
from chatgpt_auto import ChatGPTAuto
from chatgpt_yapper import ChatGPTYapper


def main() -> None:
    manager = ChatGPTYapper()
    chat_1 = ChatGPTAuto(instance_name="default", initialize=True, cookies=None, cleanup=False)
    chat_2 = ChatGPTAuto(instance_name="default", initialize=True, cookies=None, cleanup=False)
    conversation_process = None
    listener = Listener(address=("localhost", 6000), authkey=b"secret")

    while True:
        conn = listener.accept()
        try:
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
                conversation_process = manager.start_conversation_process(
                    chat_1, chat_2, initial_prompt
                )
                conn.send("Started conversation")

            elif command == "stop_conversation":
                if conversation_process is not None:
                    manager.stop.set()
                    while not manager.queue.empty():
                        manager.queue.get()
                    conn.send("Stopped conversation.")
                else:
                    conn.send("No ongoing conversation.")
            else:
                available_commands = ["quit", "is_alive", "start_conversation", "stop_conversation"]
                conn.send(
                    f"Unrecognized command. Try one of:{available_commands}"
                )

            conn.close()
        except KeyboardInterrupt:
            manager.stop.set()
            exit()

        # except ChatGPTAutoException as h:
        #     conn.send((str(h)[:250]))

        # except JavascriptException as j:
        #     conn.send((str(j)[:250]))

        # except TimeoutException as t:
        #     conn.send(str(t))
        # except Exception as e:
        #     conn.send((str(e)[:250]))

    listener.close()
    chat_1.driver.quit()
    chat_2.driver.quit()


if __name__ == "__main__":
    main()
