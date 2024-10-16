import subprocess
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from constants import *
from helper import Helper


options = Options()
driver = uc.Chrome(options, headless=False)
helper = Helper(driver)

driver.get(CHATGPT)
helper._handle_cookies(COOKIES)
sleep(.5)
driver.get(CHATGPT)


def main() -> None:
    while True:
        msg = input("You: ")

        try:
            command = helper.send_msg(msg)
            print(f"ChatGPT (command): {command}")

            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            result_txt = result.stdout.strip()
            print(f"Result: {result_txt}")

        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt. Quitting...")
