from time import sleep
from icecream import ic
from prompt_toolkit import prompt

prompt(">>> ")
n = 0
while True:
    text = "hey "
    print("\033[2K\r" + text + str(n), end="", flush=True)
    text += text
    n += 1
    sleep(0.5)
    