from typing import Final


ROOT_DIR: Final[str] =  "/home/neo/vscodeProjects/chatgpt_auto"
COOKIES: Final[str] =   f"{ROOT_DIR}/cookies.json"
COOKIES_2: Final[str] = f"{ROOT_DIR}/cookies2.json"
URLS: Final[str] =      f"{ROOT_DIR}/urls.json"
USER_DATA: Final[str] = "/home/neo/.config/google-chrome"
TTS: Final[str] =       f"{ROOT_DIR}/assets/tts"

PROMPT_TEXTAREA: Final[str] =    '//*[@id="prompt-textarea"]/p'
SEND_PROMPT_BUTTON: Final[str] = '//button[@aria-label="Send prompt"]'
NEW_CHAT_BUTTON: Final[str] =    '//button[@aria-label="New chat"]'

RULES: Final[str] = """
    RULES: ChatGPT_AUTO is for automatically running code in my terminal. 
    Python and Bash Code: You can send Python and Bash code separately, but if I request code and execution together, you should send them in separate blocks. 
    First Line of Python Code: Every Python script you send must start with a comment containing the filename. 
    Unique Filenames: Every filename must be unique to avoid overwriting existing files. 
    You can check the existing files in my project folder before writing the new Python script. 
    No Manual Confirmation: Commands you send to my terminal should not require manual confirmation. 
    If a command needs confirmation, you should add a pre-execution step to handle it. 
    Code Execution Flow: When sending Python code, you can also send the command to execute the file after creating it.
"""

PY_SCRIPTS: Final[str] = "py_scripts"

DRIVER_OPTIONS: Final[list[str]] = [
    "--log-level=3",
    "--disable-extensions",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-gpu",
    "--blink-settings=imagesEnabled=false",
]

WEBDRIVER_WAIT: Final[int] = 30

PROMPT_FORMULA: Final[str] = """


- Steps
    1. Send pip command to install the dependencies (only if you don't think I already have them)
    2. Add file name to first line of the code as a comment, e.g.: # main.py, then write code

- Constraints
    1. Never move on to a next step if there are errors
    2. All code in my computer must be saved in /home/neo/vscodeProjects/chatgpt_auto/py_scripts
    3. You are not allowed to add comments or explanations to the code other than the file name at the top

- Example
    ```bash
    pip install [dependencies]
    ```
    
    ```python
    # program_name.py
    import ...
    
    def main():
        ...
    
    if __name__ == '__main__':
        main()
    ```
"""

PROMPT_HISTORY: Final[str] = ".prompt_history.txt"