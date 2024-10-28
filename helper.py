import json
from queue import Queue
import subprocess
import threading
import traceback
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from undetected_chromedriver import Chrome
from constants import *
from custom_exceptions import HelperException
from scripts import *


class Helper:

    def __init__(self, url=CHAT, cookies=COOKIES, user_data_dir=None, is_do_cleanup=True) -> None:
        options = Options()
        for option in DRIVER_OPTIONS:
            options.add_argument(option)
        self.driver = Chrome(
            options, headless=False, no_sandbox=True, user_data_dir=user_data_dir
        )
        self.load_chatgpt_with_cookies(url, cookies)

        if is_do_cleanup:
            self.start_content_watch()
            
        self.wait = WebDriverWait(self.driver, WEBDRIVER_WAIT)
        self.queue = Queue()

    def _handle_cookies(self, cookies_file: str) -> None:
        if cookies_file is None:
            return
        with open(cookies_file, "r") as file:
            cookies = json.load(file)

        for cookie in cookies:
            if "sameSite" in cookie:
                del cookie["sameSite"]
            if "expiry" in cookie:
                cookie["expiry"] = int(cookie["expiry"])

            try:
                self.driver.add_cookie(cookie)
            except Exception:
                pass

    def _assert_stable(
        self, script, element="", wait=1, max_repeats=5, attempts=20
    ) -> int | None:
        previous_count = -1
        current_count = 0
        repeats = 0

        for _ in range(attempts):
            current_count = self.driver.execute_script(script)

            if previous_count == current_count:
                repeats += 1

            if repeats > max_repeats and current_count > 0:
                return current_count

            previous_count = current_count
            sleep(wait)
        else:
            raise HelperException("Max attempts exceeded.")

    def clean_up_page(self) -> None:
        self.driver.execute_script(CLEAN_UP_PAGE)

    def _wait_for(
        self,
        identifier: str,
        by=By.XPATH,
        attribute: str = None,
        state=EC.element_to_be_clickable,
    ) -> WebElement:

        element: WebElement = self.wait.until(state((by, identifier)))

        if attribute is not None and element.get_attribute(attribute) is None:
            raise Exception(
                f"Attribute '{attribute}' not found in element '{identifier}'."
            )

        return element

    def _get_chatgpt_response(self) -> list[tuple[str, str]] | str:
        self._assert_stable(
            GET_RESPONSE_LENGTH, element="Message", wait=0.8, max_repeats=6
        )
        messages: list[WebElement] = self.driver.find_elements(By.TAG_NAME, "article")

        if len(messages) == 0:
            return None

        last_response = messages[-1]

        code_elements: list[WebElement] = last_response.find_elements(
            By.TAG_NAME, "code"
        )

        code_elements = code_elements or []
        codes: list[tuple[str, str]] = []
        for code in code_elements:
            class_list = code.get_attribute("class") or ""
            if "language-bash" in class_list:
                bash = code.text.strip()
                codes.append(("language-bash", bash))
            elif "language-python" in class_list:
                python = code.text
                codes.append(("language-python", python))

        return codes if len(codes) > 0 else last_response.text

    def load_chatgpt_with_cookies(self, url=CHAT, cookies=COOKIES) -> None:
        self.driver.get(url)
        print(f"Got {url}")
        self.driver.delete_all_cookies()
        self._handle_cookies(cookies)
        print("Added cookies")
        sleep(0.5)
        self.driver.get(url)

    def send_prompt(self, prompt: str) -> list[tuple[str, str]] | str:
        while not self.queue.empty():
            sleep(0.5)

        self.queue.put("sending prompt")
        msg = prompt.strip().replace("\n", "")

        input_text = self._wait_for(INPUT_TEXT, state=EC.presence_of_element_located)
        input_text.click()
        input_text.send_keys(msg)

        send_button = self._wait_for(SEND_BUTTON)
        send_button.click()

        response = self._get_chatgpt_response()
        self.queue.get()
        return response

    def _run_command(self, command) -> tuple[str, bool]:
        command = command.replace("\n", " ")
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )

        stdout, stderr = process.communicate()
        is_stderror = bool(stderr)
        output = stdout if not is_stderror else stderr

        return output, is_stderror

    def handle_code(self, codes: list[tuple[str, str]]) -> str | None:
        output = None

        for code in codes:
            language = code[0]
            if language == "language-python":
                output = self._save_py_script(output, code)

            elif language == "language-bash":
                output = self._handle_bash(output, code)

        return output

    def _handle_bash(self, output: str, code: tuple[str, str]) -> str:
        command = code[1]
        if "pacman" in command:
            command += " --noconfirm"
        output, is_stderror = self._run_command(command)
        bash_output = f"BASH{(':' + command) if not is_stderror else ': '} {output} \n"
        output += bash_output
        return output

    def _save_py_script(self, output, code) -> str:
        output = ""
        py_code = code[1]
        filename = (
            py_code[py_code.find("#") + 1 : py_code.find("\n")].replace(" ", "").strip()
        )
        try:
            with open(f"{PY_SCRIPTS}/{filename}", "w") as file:
                file.write(py_code)
                python_output = f"PYTHON: '{filename}' saved. \n"
                output += python_output
        except Exception as e:
            python_output = f"PYTHON: {filename}: {e}"
            output += python_output

        return output

    def remove_stacktrace(self, exception: BaseException) -> str:
        exception_str = str(exception)
        stacktrace_start = "Stacktrace:"

        if stacktrace_start in exception_str:
            return exception_str.split(stacktrace_start, 1)[0]
        else:
            return exception_str + "\n" + traceback.format_exc()

    def _content_watch(self, is_run_once=False) -> None:
        is_run = True
        messages = 0
        while is_run:
            try:
                self._assert_stable(GET_RESPONSE_LENGTH, wait=1, max_repeats=5)
                messages = self._assert_stable(COUNT_MESSAGES, wait=1, max_repeats=5)
            except:
                continue
            if not self.queue.empty():
                continue
            if messages > 4:
                self.queue.put(messages)
                self.clean_up_page()
                self.queue.get()
                if is_run_once:
                    is_run = False
            sleep(60)

    def start_content_watch(self) -> None:
        content_watch_thread = threading.Thread(target=self._content_watch)
        content_watch_thread.daemon = True
        content_watch_thread.start()
