import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from constants import *
from helper import Helper


options = Options()
driver = uc.Chrome(options, headless=False)
helper = Helper(driver)

driver.get(OPENAI)
helper._handle_cookies(COOKIES)
driver.refresh()


def main() -> None:
    while True:
        msg = input("You: ")
        response = helper.send_msg(msg)
        print(f"ChatGPT: {response}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt. Quitting...")
