from time import perf_counter
from chatgpt_auto import ChatGPTAuto
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from constants import Paths
from icecream import ic

chat = ChatGPTAuto(cleanup=False)

prompt_history = FileHistory(Paths.PROMPT_HISTORY)
session = PromptSession(history=prompt_history)

while True:
    prompt = session.prompt(">>> ")
    
    start = perf_counter()
    response = chat.send(prompt)
    end = perf_counter()
    
    time_taken = f"{(end - start):.2f}"

    ic(response)
    ic(time_taken)
