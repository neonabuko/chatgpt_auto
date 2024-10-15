import json
import uuid
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from constants import INPUT_TEXT, SEND_BUTTON


class Helper:
    def __init__(self, driver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def _handle_cookies(self, cookies_file: str) -> None:
        with open(cookies_file, 'r') as file:
            cookies = json.load(file)

        for cookie in cookies:        
            if 'sameSite' in cookie:
                del cookie['sameSite']
            if 'expiry' in cookie:
                cookie['expiry'] = int(cookie['expiry'])

            try:
                self.driver.add_cookie(cookie)
            except Exception:
                pass


    def _generate_message_id(self) -> str:
        return str(uuid.uuid4())


    def _wait_for_full_response(self, element, wait_time=15, polling_interval=1):
        elapsed_time = 0

        while elapsed_time < wait_time:
            response = element.text

            try:
                send_button_element = self.driver.find_element(By.XPATH, SEND_BUTTON)
                if send_button_element.get_attribute('disabled'):
                    return response
            except Exception:
                sleep(polling_interval)
                elapsed_time += polling_interval

        return response


    def _get_chatgpt_response(self, msg_id: str) -> str:
        last_message_id = self._wait_for_element(
            By.XPATH, 
            f'//div[contains(text(), "ID: {msg_id}")]',
            EC.presence_of_element_located
        )
        
        response_div = last_message_id.find_element(
            By.XPATH, 
            'following::h6[text()="ChatGPT said:"]/following-sibling::div[1]'
        )
        
        return self._wait_for_full_response(response_div)



    def _wait_for_element(self, by: By, identifier: str, state=EC.element_to_be_clickable) -> EC.WebElement:
        return self.wait.until(
            state(
                (by, identifier)
            )
        )
    

    def send_msg(self, prompt: str) -> str:
        msg_id = self._generate_message_id()
        msg = f"{prompt}\nID: {msg_id}"

        input_text = self._wait_for_element(By.CSS_SELECTOR, INPUT_TEXT)
        input_text.click()

        input_text.send_keys(msg)

        send_button = self._wait_for_element(By.XPATH, SEND_BUTTON)
        send_button.click()
        sleep(1)

        return self._get_chatgpt_response(msg_id)