import json
import subprocess

from time import sleep
import time
from typing import Callable
from undetected_chromedriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from custom_exceptions import ChatGPTAutoException, ChatGPTAutoTimeoutException
from multiprocessing import Event, Process
from constants import *
from scripts import *


class ChatGPTAuto:
    """ChatGPTAuto interacts with ChatGPT using selenium.

    Parameters
    -
    initialize : bool
        For tests only. When `False`, instantiates the class with instance_name only
    cleanup : bool
        Whether to perform page cleanups or not
    cleanup_once : bool
        Clean up the page only once if `True` else clean it up periodically
    instance_name : str
        The name of the instance to be used. Instance names can be found in urls.json
    cookies : str
        The path to the cookies used to load the instance
    """

    def __init__(
        self,
        initialize: bool = True,
        cleanup: bool = True,
        cleanup_once: bool = False,
        instance_name: str = "chat_1",
        cookies: str = Paths.COOKIES,
    ) -> None:

        self.instance_name = instance_name

        if not initialize:
            return

        with open(Paths.URLS, "r") as urls_file:
            urls: dict[str, str] = json.load(urls_file)
            self._url = urls[instance_name]

        options = Options()
        for option in Variables.DRIVER_OPTIONS:
            options.add_argument(option)
        self.driver = Chrome(options, headless=False, no_sandbox=True)
        self.driver.set_page_load_timeout(10)
        self.driver.get(self._url)
        self._handle_cookies(cookies)
        sleep(0.5)
        self.driver.get(self._url)

        self._wait = WebDriverWait(self.driver, Variables.WEBDRIVER_WAIT)
        self._busy = Event()

        if cleanup:
            self._start_process(
                target=self._monitor_and_cleanup_page,
                args=(cleanup_once,),
                name="Cleanup",
                join=cleanup_once,
            )

    def send(self, prompt: str) -> list[tuple[str, str]] | str:
        """
        Sends a prompt to ChatGPT, monitors total length of text on the page, and retrieves the generated response.

        Parameters
        ----------
        prompt : str
            The input text to be sent to ChatGPT.

        Returns
        -------
        Union[list[tuple[str, str]], str]
            - Returns a list of tuples `(code_type, code_content)` if the response contains code or commands.
            - Returns a string if the response contains plain text only.
        """

        if not isinstance(prompt, str) or not prompt.strip():
            raise ChatGPTAutoException("Prompt is empty.")

        self._wait_while_busy(0.5)
        self._busy.set()

        self._wait.until(
            EC.presence_of_element_located((By.XPATH, WebElements.PROMPT_TEXTAREA))
        ).send_keys(prompt.strip().replace("\n", " "))

        self._wait.until(
            EC.element_to_be_clickable((By.XPATH, WebElements.SEND_PROMPT_BUTTON))
        ).click()
        self._busy.clear()

        self._start_process(target=self._monitor_total_text_length, name="Monitor text")

        return self._get_chatgpt_response()

    def handle_code(self, code_list: list[tuple[str, str]]) -> tuple[str, bool]:
        """
        Processes and writes Python code to files in the `/py_scripts` directory, then executes specified bash commands.

        Parameters
        ----------
        code : list[tuple[str, str]]
            Code to be written to files and/or commands to be executed.

        Returns
        -------
        A tuple containing:
            - `output` (str): Combined output of all commands and the status of Python file saves.
            - `is_stderror` (bool): True if any command produces an error; False otherwise.
        """

        cmd_output, is_stderr = "", bool(False)

        for code in code_list:
            language = code[0]
            if language == "language-python":
                py_script = code[1]
                filename = py_script[
                    py_script.find("#") + 1 : py_script.find("\n")
                ].strip()
                with open(f"{Paths.PY_SCRIPTS}/{filename}", "w") as file:
                    file.write(py_script)
                    output = f"'{filename}' saved."
                    print(output)
                    cmd_output += f" {output}"

            elif language == "language-bash":
                command = code[1]
                process = subprocess.Popen(
                    command.strip(),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    universal_newlines=True,
                )

                stdout, stderr = process.communicate()
                is_stderr = bool(stderr)
                stdout = stdout if not is_stderr else stderr

                if "Requirement already satisfied" in stdout:
                    stdout = stdout[: stdout.find("\n")]

                output = f"{command}: {stdout.strip()}"
                print(output)
                cmd_output += f" {output}"

        return cmd_output, is_stderr

    def _handle_cookies(self, cookies_path: str) -> None:
        if cookies_path is None:
            return
        with open(cookies_path, "r") as file:
            cookies = json.load(file)

        for cookie in cookies:
            if "sameSite" in cookie:
                del cookie["sameSite"]
            if "expiry" in cookie:
                cookie["expiry"] = int(cookie["expiry"])
            try:
                self.driver.add_cookie(cookie)
            except:
                pass

    def _get_chatgpt_response(self) -> list[tuple[str, str]] | str:
        print("Awaiting response")
        self._busy.set()

        while self.driver.execute_script(Scripts.IS_GENERATING_RESPONSE):
            sleep(0.5)
        messages: list[WebElement] = self.driver.find_elements(By.TAG_NAME, "article")
        if messages is None or len(messages) == 0:
            raise ChatGPTAutoException("Found no messages in current chat")

        self._busy.clear()

        print("Retrieving response")
        last_response = messages[-1]

        code_elements: list[WebElement] = (
            last_response.find_elements(By.TAG_NAME, "code") or []
        )

        code_found = []
        for code in code_elements:
            class_list = code.get_attribute("class")
            if class_list is None:
                break
            if "language-bash" in class_list:
                bash = code.text.strip()
                code_found.append(("language-bash", bash))
            elif "language-python" in class_list:
                python = code.text
                code_found.append(("language-python", python))

        return code_found if len(code_found) > 0 else last_response.text

    def _get_stable_output_from_script(
        self,
        script: str,
        interval: int | float = 1,
        timeout: int | float = 30,
        coincidences: int = 5,
    ) -> int:
        previous_count = -1
        current_count, repeats = 0, 0
        start = time.time()
        while repeats < coincidences:
            elapsed_time = time.time() - start

            if elapsed_time > timeout:
                raise ChatGPTAutoTimeoutException(timeout=timeout)

            current_count = self.driver.execute_script(script)

            if previous_count == current_count:
                repeats += 1

            previous_count = current_count
            sleep(interval)

        return current_count if isinstance(current_count, int) else -1

    def _start_process(
        self, target: Callable, args: tuple = (), name: str = "process", join=False
    ) -> Process:
        process = Process(target=target, args=args)
        process.daemon = True
        process.name = name
        process.start()
        if join:
            process.join()
        return process

    def _monitor_total_text_length(self) -> None:
        text_length: int = self._get_stable_output_from_script(
            Scripts.GET_ALL_TEXT_LENGTH, interval=0.5, coincidences=5
        )

        if text_length > 100_000:
            self._wait_while_busy(1)
            self._busy.set()
            print("Starting new chat")
            self._wait.until(
                EC.element_to_be_clickable((By.XPATH, WebElements.NEW_CHAT_BUTTON))
            ).click()
            self._busy.clear()

        if (
            self.driver.current_url != self._url
            and self.driver.current_url != "https://chatgpt.com/?model=auto"
        ):
            self._url = self.driver.current_url
            with open(Paths.URLS, "r") as file:
                urls: dict[str, str] = json.load(file)
                urls[self.instance_name] = self._url

            with open(Paths.URLS, "w") as file:
                json.dump(urls, file, indent=4)

    def _monitor_and_cleanup_page(self, cleanup_once: bool = False) -> None:
        is_generating_response = False
        while True:
            try:
                is_generating_response = self._get_stable_output_from_script(
                    Scripts.IS_GENERATING_RESPONSE, interval=0.5, coincidences=3
                )
            except:
                try:
                    self.driver.refresh()
                except TimeoutException:
                    print("Timeout when refreshing")
                    break
                continue

            if not is_generating_response:
                self._wait_while_busy(1)
                print("Cleaning up")
                self._busy.set()
                self.driver.execute_script(Scripts.CLEAN_UP_PAGE)
                self._busy.clear()
                if cleanup_once:
                    break
                sleep(30)

    def _wait_while_busy(self, interval: int | float) -> None:
        while self._busy.is_set():
            sleep(interval)
