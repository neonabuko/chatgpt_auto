import json
from typing import Any, Callable, Optional
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from undetected_chromedriver import Chrome
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

    def clean_up_page(self, attempts=40, interval=1) -> None:
        previous_count = -1
        for _ in range(attempts):
            current_count = self.driver.execute_script(COUNT_ARTICLES)

            if current_count == previous_count:
                removed = self.driver.execute_script(CLEAN_UP_PAGE)
                print(f"Cleaned up {str(removed)} articles")
                break

            previous_count = current_count
            sleep(interval)
        else:
            print("Could not clean up page, article count unstable")

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
        header = "_try_for:"
        for attempt in range(attempts):
            try:
                out = method()
                if out is None:
                    raise HelperException("Out is none")

                if type(out) == list and len(out) == 0:
                    raise HelperException("Out is empty")

                if expected_attribute is not None:
                    if out.get_attribute(expected_attribute) is None:
                        raise HelperException(
                            f"No such attribute: {expected_attribute}"
                        )
                    else:
                        print(f"{header} Found attribute {expected_attribute}")

                while (
                    wait_generate
                    and GENERATING
                    in self.driver.find_element(By.XPATH, "/html/body/div[2]").text
                    or ""
                ):
                    print(f"{header} Generating response...")
                    sleep(1)

                print(f"{header} Returning output...")
                return out

            except Exception as e:
                print(str(e))
                if attempt < attempts:
                    sleep(wait_amount)

    def _get_chatgpt_commands(self) -> list[str]:
        messages: list[WebElement] = self._try_for(
            lambda: self.driver.find_elements(By.TAG_NAME, "article"),
            wait_generate=True,
        )
        
        last_response = messages[-1]

        codes: list[WebElement] = self._try_for(
            lambda: last_response.find_elements(By.TAG_NAME, "code"), attempts=2
        )

        cmds = []
        for code in codes:
            classList = code.get_attribute('class')
            if classList is not None and 'language-bash' in classList:
                cmds.append(code.text.strip())

        return cmds

    def load_chatgpt_with_cookies(self) -> None:
        self.driver.get(CHAT)
        print(f"Got {CHAT}")
        self._handle_cookies(COOKIES)
        print("Added cookies")
        sleep(0.5)
        self.driver.get(CHAT)

    def send_prompt(self, prompt: str) -> list[str]:
        msg = prompt.strip().replace("\n", "")

        input_text = self._wait_for(INPUT_TEXT, state=EC.presence_of_element_located)
        input_text.click()
        input_text.send_keys(msg)

        send_button = self._wait_for(SEND_BUTTON)
        send_button.click()

        return self._get_chatgpt_commands()
