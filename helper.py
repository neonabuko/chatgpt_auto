import json
import os
import subprocess
import time
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
        self.wait = WebDriverWait(self.driver, WAIT)

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


    def clean_up_page(self) -> None:
        previous_count = -1
        repeats = 0
        attempts = 20
        
        for _ in range(attempts):
            current_count = self.driver.execute_script(COUNT_MESSAGES)

            if previous_count == current_count:
                repeats += 1

            if repeats > 5:
                break

            previous_count = current_count
            sleep(1)
        
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

    def _try_for(
        self,
        method: Callable,
        attempts=10,
        wait_generate=False,
        expected_attribute=None,
        wait_amount=1,
    ) -> Optional[Any]:
        header = "_try_for() ->"
        for attempt in range(attempts):
            try:
                out = method()
                if out is None:
                    raise HelperException("out is none")

                if type(out) == list and len(out) == 0:
                    raise HelperException("out is empty")

                if expected_attribute is not None:
                    if out.get_attribute(expected_attribute) is None:
                        raise HelperException(
                            f"No such attribute: {expected_attribute}"
                        )
                    else:
                        print(f"{header} Found attribute {expected_attribute}")

                if wait_generate:
                    generating_found = False
                    while True:
                        text = self.driver.find_element(By.XPATH, "/html/body/div[2]").text
                        if GENERATING not in text and generating_found:
                            break
                        if GENERATING in text and not generating_found:
                            generating_found = True
                            print(f"{header} Generating response...")
                        sleep(1)

                print(f"{header} Returning output...")
                return out

            except Exception as e:
                print(str(e))
                if attempt < attempts:
                    sleep(wait_amount)

    def _get_chatgpt_response(self) -> list[tuple[str, str]]:
        messages: list[WebElement] = self._try_for(
            lambda: self.driver.find_elements(By.TAG_NAME, "article")
        )
        
        last_response = messages[-1]

        code_elements: list[WebElement] = self._try_for(
            lambda: last_response.find_elements(By.TAG_NAME, "code"), attempts=2
        )

        codes: list[tuple[str, str]] = []
        for code in code_elements:
            class_list = code.get_attribute('class')
            if class_list is not None:
                if 'language-bash' in class_list:
                    bash = code.text.strip()
                    codes.append(('language-bash', bash))
                elif 'language-python' in class_list:
                    python = code.text
                    codes.append(('language-python', python))

        return codes

    def load_chatgpt_with_cookies(self) -> None:
        self.driver.get(CHAT)
        print(f"Got {CHAT}")
        self._handle_cookies(COOKIES)
        print("Added cookies")
        sleep(0.5)
        self.driver.get(CHAT)

    def send_prompt(self, prompt: str) -> list[tuple[str, str]]:
        msg = prompt.strip().replace("\n", "")

        input_text = self._wait_for(INPUT_TEXT, state=EC.presence_of_element_located)
        input_text.click()
        input_text.send_keys(msg)

        send_button = self._wait_for(SEND_BUTTON)
        send_button.click()

        sleep(10)
        return self._get_chatgpt_response()


    def _run_command(self, command) -> tuple[str, bool]:
        printf(f"-> Command:\n{command}")
        completed_process = subprocess.run(
            command, shell=True, capture_output=True, text=True
        )

        is_stderror = completed_process.stderr != ""
        output = completed_process.stderr if is_stderror else completed_process.stdout

        return output, is_stderror

    
    def _ensure_unique_filename(self, filename: str) -> str:
        if os.path.exists(filename):
            base, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            filename = f"{base}_{timestamp}{ext}"
        return filename
    

    def handle_codes(self, codes: list[tuple[str, str]]) -> str:
        prompt = ""
        for code in codes:
            if code is None:
                continue
            if code[0] == "language-python":
                py_code = code[1]
                filename = py_code[py_code.find("#")+1 : py_code.find("\n")].replace(
                    " ", ""
                ).strip()
                filename = self._ensure_unique_filename(filename)
                try:
                    with open(filename, "w") as file:
                        file.write(py_code)
                        prompt += f"PYTHON: '{filename}' successfully written to file.\n"
                except Exception as e:
                    prompt += f"PYTHON: {filename}: {e}"

            elif code[0] == "language-bash":
                command = code[1]
                output, is_stderror = self._run_command(command)
                prompt += f"BASH{(': ' + command) if not is_stderror else ': '} {output}\n"

        return prompt

    
    def remove_stacktrace(self, exception: BaseException) -> str:
        exception_str = str(exception)
        stacktrace_start = "Stacktrace:"
        
        if stacktrace_start in exception_str:
            return exception_str.split(stacktrace_start, 1)[0]
        else:
            return exception_str + "\n" + traceback.format_exc()
 