import json
from typing import Callable
import uuid
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from constants import CHECK_ARTICLES_SCRIPT, CLEAN_UP_SCRIPT, INPUT_TEXT, SEND_BUTTON, WAIT


class Helper:
    def __init__(self, driver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT)


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


    # TODO Use "ChatGPT is generating a response..." string found on the
    # webpage as reference


    def clean_up_page(self, attempts=40, interval=1) -> None:
        previous_count = -1
        for _ in range(attempts):
            current_count = self.driver.execute_script(CHECK_ARTICLES_SCRIPT)
            print(f"Current article count: {current_count}")
            
            if current_count == previous_count:
                print("Article count is stable. Cleaning up the page...")
                self.driver.execute_script(CLEAN_UP_SCRIPT)
                break
            
            previous_count = current_count
            sleep(interval)
        else:
            print("No stable article count found within the specified attempts.")


    def _wait_for(
        self,
        identifier: str,
        by=By.XPATH,
        attribute: str = None,
        state=EC.element_to_be_clickable,
    ) -> EC.WebElement:

        element: EC.WebElement = self.wait.until(state((by, identifier)))

        if attribute and element.get_attribute(attribute) is None:
            raise Exception(f"Attribute '{attribute}' not found in element '{identifier}'.")

        return element


    def _try_for(
        self,
        method: Callable,
        expected_content: str = None,
        attempts: int = 10,
        wait: int = 1,
    ) -> EC.WebElement | None:
        for _ in range(attempts):
            try:
                out = method()
                if out is None:
                    raise Exception

                text = out.text.strip()
                if not expected_content or expected_content in text:
                    return out

            except Exception:
                pass

            sleep(wait)


    def _get_chatgpt_response(
        self, msg_id: str, expect_code=False, expected_content: str = None
    ) -> EC.WebElement:
        last_prompt = self._wait_for(
            f'//div[contains(text(), "ID: {msg_id}")]',
            state=EC.presence_of_element_located,
        )

        response_xpath = 'following::h6[text()="ChatGPT said:"]/following-sibling::div[1]'

        response = self._try_for(
            lambda: last_prompt.find_element(By.XPATH, response_xpath),
            expected_content=expected_content,
        )

        code_xpath = f"{response_xpath}//code[@class]"

        code = self._try_for(
            lambda: last_prompt.find_element(By.XPATH, code_xpath),
        )

        return code if expect_code else response


    def send_prompt(self, prompt: str, expect_code=False) -> str:
        msg_id = str(uuid.uuid4())
        msg = f"{prompt} ID: {msg_id}".strip()

        input_text = self._wait_for(
            INPUT_TEXT, by=By.CSS_SELECTOR, state=EC.presence_of_element_located
        )
        input_text.click()
        input_text.send_keys(msg)

        send_button = self._wait_for(SEND_BUTTON)
        send_button.click()

        return self._get_chatgpt_response(
            msg_id, expect_code, expected_content="CODE COMPLETE"
        ).text.strip()
