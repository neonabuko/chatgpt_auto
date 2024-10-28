from multiprocessing.connection import Client

def send_command(command, address=('localhost', 6000), authkey=b'secret'):
    conn = Client(address, authkey=authkey)
    conn.send(command)
    response = conn.recv()
    conn.close()
    return response

if __name__ == '__main__':
    while True:
        try:
            command = str(input('> '))
            response = send_command(command)
            print(response)
        except Exception as e:
            print(str(e)[:300])
            continue
