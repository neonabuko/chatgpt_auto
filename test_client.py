from multiprocessing.connection import Client
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from constants import Paths

def send_command(command, address=('localhost', 6000), authkey=b'secret'):
    conn = Client(address, authkey=authkey)
    conn.send(command)
    response = conn.recv()
    conn.close()
    return response

if __name__ == '__main__':
    prompt_history = FileHistory(Paths.CLIENT_HISTORY)
    session = PromptSession(history=prompt_history)
    while True:
        try:
            command = session.prompt(">>> ")
            response = send_command(command)
            print(response)
        except Exception as e:
            print(str(e)[:300])
            continue
