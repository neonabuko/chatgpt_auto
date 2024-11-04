# from multiprocessing import Process
# from time import sleep
# import os
# import sys


# def main() -> None:
#     start_dots_process()
#     try:
#         while True:
#             sleep(1)
#     except KeyboardInterrupt:
#         print("\nProcess interrupted.")


# def start_dots_process() -> None:
#     dots_process = Process(target=dots)
#     dots_process.daemon = True
#     dots_process.start()


# def dots() -> None:
#     for _ in range(2):
#         dot = "."
#         for _ in range(3):
#             message = f"\rRetrieving response{dot}"
#             os.write(sys.stdout.fileno(), message.encode())
#             dot += "."
#             sleep(0.5)
#         clear_line()
#     clear_line()


# def clear_line() -> None:
#     os.write(sys.stdout.fileno(), b"\r" + b" " * 50 + b"\r")


# if __name__ == "__main__":
#     main()


import os
from chatgpt_auto import ChatGPTAuto


def test_should_save_python_script():
    chatgpt = ChatGPTAuto(initialize=False)
    script_name = "test.py"
    script = f"# {script_name}\nprint('JooJ')"
    code = [('language-python', script)]
    chatgpt.handle_code(code)

    assert script_name in os.listdir('py_scripts')

    with open(f"py_scripts/{script_name}", 'r') as saved_script:
        saved_script_content = saved_script.read()
    
    assert saved_script_content == script, (saved_script_content, script)


files = os.listdir('py_scripts')

print(files)