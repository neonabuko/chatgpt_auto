import json
from multiprocessing import Manager, Process
import subprocess
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from undetected_chromedriver import Chrome
from constants import *
from custom_exceptions import ChatGPTAutoException
from scripts import *


class ChatGPTAuto:
    """ChatGPTAuto interacts with ChatGPT using selenium.
    
    Parameters
    -
    initialize : bool
        For tests only. When `False`, instantiates the class without the driver.
    cleanup : bool
        Whether to clean up the page at all or not
    cleanup_once : bool
        Clean up the page only once if `True` else clean it up periodically
    instance_name : str
        The name of the instance to be used. Instance names can be found in urls.json
    cookies : str
        The path to the cookies used to load the instance
    """

    def __init__(
        self,
        initialize=True,
        cleanup=True,
        cleanup_once=False,
        instance_name="chat_1",
        cookies=COOKIES,
    ) -> None:
        if not initialize:
            return
        self.instance_name = instance_name
        self._page_load_timeout = 10
        self._queue = Manager().Queue()

        self._url = self._get_instance_url(instance_name)
        self._initialize_driver(cookies)
        self._wait = WebDriverWait(self.driver, WEBDRIVER_WAIT)

        if cleanup:
            self._start_monitor_and_cleanup_process(cleanup_once=cleanup_once)

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

        Notes
        -----
        This method:
            1. Sends the prompt to ChatGPT.
            2. Initiates monitoring of total text length on the page.
            3. Retrieves the response from ChatGPT.
        """

        self._type_and_send_prompt(prompt)
        self._start_monitor_total_text_length()
        return self._get_last_chatgpt_response()

    def handle_code(self, code: list[tuple[str, str]]) -> tuple[str, bool]:
        """
        Processes and writes Python code to files in the `/py_scripts` directory, then executes specified bash commands.

        Parameters
        ----------
        code : list[tuple[str, str]]
            Code to be written to files and/or commands to be executed.

        Returns
        -------
        tuple
            A tuple containing:
                - `output` (str): Combined output of all commands and the status of Python file saves.
                - `is_stderror` (bool): True if any command produces an error; False otherwise.

        Notes
        -----
        This function automates code storage and command execution, returning details about success and errors.
        """

        output, is_stderror = "", bool(False)

        for code in code:
            language = code[0]
            if language == "language-python":
                output = self._save_py_script(output, code)

            elif language == "language-bash":
                output, is_stderror = self._handle_bash(output, code)

        return output, is_stderror

    def _type_and_send_prompt(self, prompt: str) -> None:
        assert prompt is not None and prompt != "", "Prompt is empty."

        while not self._is_queue_empty():
            sleep(0.5)
        self._queue.put("sending prompt")

        input_text = self._wait_get_webelement(
            PROMPT_TEXTAREA, state=EC.presence_of_element_located
        )
        input_text.click()
        input_text.send_keys(prompt.strip().replace("\n", ""))

        send_button = self._wait_get_webelement(SEND_PROMPT_BUTTON)
        send_button.click()

        self._clear_queue()

    def _get_instance_urls(self, json_path: str = URLS) -> dict[str, str]:
        with open(json_path, "r") as file:
            urls: dict = json.load(file)
        return urls

    def _get_instance_url(self, instance_name: str, json_path: str = URLS) -> str:
        urls: dict[str, str] = self._get_instance_urls(json_path=json_path)
        return urls.get(
            instance_name, f"Chat instance '{instance_name}' not found in urls.json"
        )

    def _update_instance_url(
        self, instance_name: str, new_url: str, json_path: str = URLS
    ) -> None:
        urls: dict[str, str] = self._get_instance_urls(json_path=json_path)
        urls[instance_name] = new_url

        with open(json_path, "w") as file:
            json.dump(urls, file, indent=4)

    def _initialize_driver(self, cookies: str) -> None:
        options = Options()
        for option in DRIVER_OPTIONS:
            options.add_argument(option)
        self.driver = Chrome(options, headless=False, no_sandbox=True)
        self.driver.set_page_load_timeout(self._page_load_timeout)
        self._load_chatgpt_with_cookies(cookies)

    def _load_chatgpt_with_cookies(self, cookies=COOKIES) -> None:
        self.driver.get(self._url)
        self.driver.delete_all_cookies()
        self._handle_cookies(cookies)
        sleep(0.5)
        self.driver.get(self._url)

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

    def _get_last_chatgpt_response(self) -> list[tuple[str, str]] | str:
        print("Awaiting response")
        self._assert_script_output_stable(
            GET_LAST_RESPONSE_LENGTH, wait=0.8, max_repeats=6
        )
        messages: list[WebElement] = self.driver.find_elements(By.TAG_NAME, "article")

        if isinstance(messages, list) and len(messages) == 0 or messages is None:
            raise ChatGPTAutoException("Empty message")

        print("Retrieving response")
        last_response = messages[-1]

        code_elements: list[WebElement] = last_response.find_elements(
            By.TAG_NAME, "code"
        )

        code_elements = code_elements or []
        codes = self._format_code_elements(code_elements)

        return codes if len(codes) > 0 else last_response.text

    def _wait_get_webelement(
        self,
        identifier: str,
        by=By.XPATH,
        attribute: str = None,
        state=EC.element_to_be_clickable,
    ) -> WebElement:

        element: WebElement = self._wait.until(state((by, identifier)))

        if attribute is not None and element.get_attribute(attribute) is None:
            raise ChatGPTAutoException(
                f"Attribute '{attribute}' not found in element '{identifier}'."
            )

        return element

    def _format_code_elements(
        self, elements: list[WebElement]
    ) -> list[tuple[str, str]]:
        codes: list[tuple[str, str]] = []
        for element in elements:
            class_list = element.get_attribute("class") or ""
            if "language-bash" in class_list:
                bash = element.text.strip()
                codes.append(("language-bash", bash))
            elif "language-python" in class_list:
                python = element.text
                codes.append(("language-python", python))

        return codes

    def _assert_script_output_stable(
        self, script, wait=1, max_repeats=5, attempts=20
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
            sleep(wait)
        else:
            raise ChatGPTAutoException("Max attempts exceeded.")

    def _handle_bash(
        self, output: str | None, code: tuple[str, str]
    ) -> tuple[str, bool]:
        command = code[1]
        command_output, is_stderror = self._run_command(command)
        bash_output = f"{command}: {command_output}"
        output = output or ""
        output += f"{bash_output}"
        return output, is_stderror

    def _run_command(self, command: str):
        command = command.replace("\n", " ")
        if "pacman" in command:
            command += " --noconfirm"
        print(f"> {command}")
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
        stdout = stdout if not is_stderror else stderr

        formatted_command_output = self._format_command_output(stdout)
        print(f"\t{formatted_command_output}")
        return formatted_command_output, is_stderror

    def _format_command_output(self, output: str) -> str:
        if "Requirement already satisfied" in output:
            output = output[: output.find("\n")]
        return output.strip()

    def _save_py_script(self, output, code) -> str:
        output = ""
        py_code = code[1]
        filename = py_code[py_code.find("#") + 1 : py_code.find("\n")].strip()
        try:
            with open(f"{PY_SCRIPTS}/{filename}", "w") as file:
                file.write(py_code)
                python_output = f"'{filename}' saved."
                output += python_output
                print(python_output)
        except Exception as e:
            python_output = f"{filename}: {e}"
            output += python_output
            print(python_output)

        return output

    def _start_monitor_and_cleanup_process(self, cleanup_once=False) -> None:
        p = Process(target=self._monitor_and_cleanup_page, args=(cleanup_once,))
        p.daemon = True
        p.name = "Monitor and Cleanup"
        p.start()
        if cleanup_once:
            p.join()

    def _start_monitor_total_text_length(self) -> None:
        p = Process(target=self._monitor_total_text_length)
        p.daemon = True
        p.name = "Monitor Text Length"
        p.start()

    def _monitor_total_text_length(self) -> None:
        text_length: int = self._assert_script_output_stable(
            GET_ALL_TEXT_LENGTH, wait=0.5, max_repeats=5
        )

        if text_length > 100_000:
            while not self._is_queue_empty():
                sleep(0.5)
            self._queue.put("starting new chat")
            print("Starting new chat")
            self._start_new_chat()
            self._clear_queue()

    def _start_new_chat(self) -> None:
        new_chat_button = self._wait_get_webelement(
            identifier=NEW_CHAT_BUTTON, by=By.XPATH
        )
        new_chat_button.click()

        while self.driver.current_url == self._url:
            sleep(0.5)

        self._url = self.driver.current_url
        self._update_instance_url(self.instance_name, new_url=self._url)

    def _monitor_and_cleanup_page(self, cleanup_once=False) -> None:
        exceptions = 0
        while True:
            if not self._is_messages_stable():
                is_refreshed = self._refresh_driver(exceptions)
                if not is_refreshed:
                    break
                continue
            if self._is_queue_empty():
                print("Cleaning up.")
                self._cleanup_page()
                if cleanup_once:
                    break
                sleep(30)

    def _is_messages_stable(self) -> bool:
        try:
            messages = self._assert_script_output_stable(
                COUNT_MESSAGES, wait=0.5, max_repeats=3
            )
            self._assert_script_output_stable(
                GET_LAST_RESPONSE_LENGTH, wait=0.5, max_repeats=3
            )
            return messages > 2
        except:
            return False

    def _refresh_driver(self) -> bool | None:
        try:
            self.driver.refresh()
        except TimeoutException:
            print("Timeout when refreshing. Terminating cleanup process.")
            return bool(False)

    def _cleanup_page(self) -> None:
        self._queue.put("cleaning up")
        self.driver.execute_script(CLEAN_UP_PAGE)
        self._clear_queue()

    def _clear_queue(self) -> None:
        while not self._is_queue_empty():
            self._queue.get()

    def _is_queue_empty(self) -> bool:
        return self._queue.qsize() == 0
