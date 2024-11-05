import json
from undetected_chromedriver import Chrome, ChromeOptions

from constants import URLS

options = ChromeOptions()
driver = Chrome(options)

def monitor_url(url: str) -> None:
    new_url = driver.current_url
    if new_url != url:
        url = new_url
        with open(URLS, "r") as file:
            urls: dict = json.load(file)
            urls["chat_1"] = url

        with open(URLS, "w") as file:
            json.dump(urls, file, indent=4)

google = "https://google.com"

driver.get("https://chatgpt.com")
monitor_url(google)