import subprocess
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from constants import *
from helper import Helper


def _print_with(text, char="\n"):
    print(char + text)


def main() -> None:
    options = Options()
    options.add_argument("--log-level=3")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--blink-settings=imagesEnabled=false")    
    driver = uc.Chrome(options, headless=False, no_sandbox=True)
    helper = Helper(driver)

    driver.get(CHATGPT)
    helper._handle_cookies(COOKIES)
    sleep(.5)
    driver.get(CHATGPT)
    
    is_error = False

    while True:
        if not is_error:
            prompt = "CHATGPT_AUTO "
            prompt += str(input("\n-> You: "))

        try:
            response = helper.send_prompt(prompt, expect_code=True)

            if "CODE COMPLETE" in response:
                cmd = response.replace("CODE COMPLETE", "").strip()
                _print_with(f"-> Command:\n{cmd}")
                out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if out.stderr != "":
                    out = out.stderr.strip()
                    prompt = out
                    _print_with(f"-> Error:\n{out}")
                    is_error = True

                else:
                    out = out.stdout.strip()
                    _print_with(f"-> Output:\n{out}")
                    is_error = False
            
            else:
                _print_with(f"-> ChatGPT: {response}")

        except KeyboardInterrupt:
            _print_with("Received keyboard interrupt. Quitting...")
            exit()

        except Exception as e:
            exception = str(e)
            _print_with(exception)


if __name__ == '__main__':
    main()

