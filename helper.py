import json
import queue
import subprocess
import threading
import traceback
from typing import Any, Callable, Optional
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from undetected_chromedriver import Chrome
from chat_utils import printf
from constants import *
from custom_exceptions import HelperException


class Helper:
    def __init__(self) -> None:
        options = Options()
        for option in DRIVER_OPTIONS:
            options.add_argument(option)
        self.driver = Chrome(options, headless=False, no_sandbox=True)
        self.wait = WebDriverWait(self.driver, WEBDRIVER_WAIT)

    def _handle_cookies(self, cookies_file: str) -> None:
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

            if repeats > max_repeats:
                return current_count

            previous_count = current_count
            # print(f"Current {element} count: {current_count}", end="\r", flush=True)
            sleep(wait)
        else:
            raise HelperException("Max attempts exceeded.")

    def clean_up_page(self) -> None:
        self._assert_stable(COUNT_MESSAGES, element="message", wait=0.9, max_repeats=4)
        print("Cleaning up page")
        removed = self.driver.execute_script(CLEAN_UP_PAGE)
        print(f"Cleaned up {removed} messages")

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
        self._assert_stable(GET_MESSAGE_LENGTH, element="character", wait=0.8, max_repeats=4)
        messages: list[WebElement] = self.driver.find_elements(By.TAG_NAME, "article")

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

    def load_chatgpt_with_cookies(self) -> None:
        self.driver.get(CHAT)
        print(f"Got {CHAT}")
        self._handle_cookies(COOKIES)
        print("Added cookies")
        sleep(0.5)
        self.driver.get(CHAT)

    def send_prompt(self, prompt: str) -> list[tuple[str, str]] | str:
        msg = prompt.strip().replace("\n", "")

        input_text = self._wait_for(INPUT_TEXT, state=EC.presence_of_element_located)
        input_text.click()
        input_text.send_keys(msg)

        send_button = self._wait_for(SEND_BUTTON)
        send_button.click()

        sleep(1)
        return self._get_chatgpt_response()

    def _run_command(self, command) -> tuple[str, bool]:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )

        output = []
        is_stderror = False

        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()

            if stdout_line:
                output.append(stdout_line.strip())
                print(stdout_line.strip())
            if stderr_line:
                output.append(stderr_line.strip())
                is_stderror = True
                print(stderr_line.strip())

            if process.poll() is not None:
                break

        stdout, stderr = process.communicate()
        if stdout:
            output.append(stdout.strip())
        if stderr:
            output.append(stderr.strip())
            is_stderror = True

        output_str = "\n".join(output)

        return output_str, is_stderror

    def handle_codes(self, codes: list[tuple[str, str]]) -> tuple[str, bool]:
        prompt = ""
        steps = len(codes)
        is_has_errors = False

        for code in codes:
            if code is None:
                steps -= 1
                continue

            step = f"Step {codes.index(code)+1}/{steps}"

            if code[0] == "language-python":
                py_code = code[1]
                filename = (
                    py_code[py_code.find("#") + 1 : py_code.find("\n")]
                    .replace(" ", "")
                    .strip()
                )
                try:
                    with open("py_scripts/" + filename, "w") as file:
                        file.write(py_code)
                        python_output = (
                            f"PYTHON: '{filename}' successfully written to file. \n"
                        )
                        prompt += python_output
                        printf(f"{step}:\n{python_output}")
                except Exception as e:
                    prompt += f"PYTHON: {filename}: {e}"

            elif code[0] == "language-bash":
                command = code[1]
                if "pacman" in command:
                    command += " --noconfirm"
                printf(f"{step}: {command}")
                output, is_stderror = self._run_command(command)
                is_has_errors = is_stderror
                bash_output = (
                    f"BASH{(': ' + command) if not is_stderror else ': '} {output} \n"
                )
                prompt += bash_output
                printf(bash_output)

        return prompt, is_has_errors

    def remove_stacktrace(self, exception: BaseException) -> str:
        exception_str = str(exception)
        stacktrace_start = "Stacktrace:"

        if stacktrace_start in exception_str:
            return exception_str.split(stacktrace_start, 1)[0]
        else:
            return exception_str + "\n" + traceback.format_exc()


    def _content_watch(self, messages_queue) -> None:
        while True:
            messages = self.driver.execute_script(COUNT_MESSAGES)
            messages_queue.put(messages)
            if self.get_messages_length(messages_queue) > 4:
                self.clean_up_page()
            sleep(5)


    def start_content_watch(self, messages_queue) -> None:
        content_watch_thread = threading.Thread(target=self._content_watch, args=(messages_queue, ))
        content_watch_thread.daemon = True
        content_watch_thread.start()


    def get_messages_length(self, messages_queue) -> Any | None:
        if not messages_queue.empty():
            return messages_queue.get()
        return None