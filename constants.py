ROOT_DIR = "/home/neo/vscodeProjects/chatgpt_auto"
COOKIES = ROOT_DIR + "/cookies.json"
COOKIES_2 = ROOT_DIR + "/cookies2.json"
CHAT = "https://chatgpt.com/c/671725db-b7b8-800b-9dca-8c6a9dff7bba"
CHAT_2 = "https://chatgpt.com/c/671cd149-99c8-800e-8555-bf669912fa61"

DRIVER_OPTIONS = [
    "--log-level=3",
    "--disable-extensions",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-gpu",
    "--blink-settings=imagesEnabled=false",
]

USER_DATA_1 = "/home/neo/.config/google-chrome"
USER_DATA_2 = "/home/neo/.config/google-chrome/Profile\ 2"

TTS = f"{ROOT_DIR}/assets/tts"

INPUT_TEXT = '//*[@id="prompt-textarea"]/p'
SEND_BUTTON = '//button[@aria-label="Send prompt"]'
WEBDRIVER_WAIT = 30

RULES = "RULES: ChatGPT_AUTO is for automatically running code in my terminal. Python and Bash Code: You can send Python and Bash code separately, but if I request code and execution together, you should send them in separate blocks. First Line of Python Code: Every Python script you send must start with a comment containing the filename. Unique Filenames: Every filename must be unique to avoid overwriting existing files. You can check the existing files in my project folder before writing the new Python script. No Manual Confirmation: Commands you send to my terminal should not require manual confirmation. If a command needs confirmation, you should add a pre-execution step to handle it. Code Execution Flow: When sending Python code, you can also send the command to execute the file after creating it."

PROMPT_HEADER = "CHATGPT_AUTO"

PY_SCRIPTS = 'py_scripts'