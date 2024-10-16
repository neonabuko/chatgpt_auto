import json
import uuid
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from constants import INPUT_TEXT, SEND_BUTTON, WAIT


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


    def _generate_message_id(self) -> str:
        return str(uuid.uuid4())


    def _wait_for(
        self,
        by: By,
        identifier: str,
        attribute: str = None,
        state=EC.element_to_be_clickable,
    ) -> EC.WebElement:

        element: EC.WebElement = self.wait.until(state((by, identifier)))

        if attribute:
            if not element.get_attribute(attribute):
                raise Exception(f"Attribute '{attribute}' not found in element '{identifier}'.")
        
        return element


    def _try_action(self, action, check_str_is_empty=False, attempts=5, wait=1):
        for _ in range(attempts):
            try:
                out = action()
                if not check_str_is_empty or out.text.strip() != "":
                    return out
            except Exception:
                pass
            sleep(wait)


    def _get_chatgpt_response(self, msg_id: str, code=False) -> str:
        last_prompt = self._wait_for(
            By.XPATH,
            f'//div[contains(text(), "ID: {msg_id}")]',
            state=EC.presence_of_element_located
        )

        response_xpath = (
            'following::h6[text()="ChatGPT said:"]/following-sibling::div[1]'
        )

        response = self._try_action(
            lambda: last_prompt.find_element(
                By.XPATH, 
                f'{response_xpath}//code[@class]' if code else response_xpath
            )
        )
        response_txt: str = response.text
        return response_txt.strip() if response else ""


    def send_msg(self, prompt: str) -> str:
        msg_id = self._generate_message_id()
        msg = f"{prompt}    ID: {msg_id}"

        input_text = self._wait_for(By.CSS_SELECTOR, INPUT_TEXT, state=EC.presence_of_element_located)
        input_text.click()
        input_text.send_keys(msg)

        send_button = self._wait_for(By.XPATH, SEND_BUTTON)
        send_button.click()

        return self._get_chatgpt_response(msg_id, code=True)
