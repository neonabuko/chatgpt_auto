import os
from queue import Queue
import threading
from time import sleep
from typing import Callable
from selenium.common.exceptions import JavascriptException
from gtts import gTTS
from constants import CHAT, CHAT_2, COOKIES, TTS
from custom_exceptions import HelperException
from helper import Helper
from pydub import AudioSegment
from sys import argv


if len(argv) < 2:
    print(
        "Usage: python main.py <lang: str> <speed: float>\nExample: python main.py pt 1.7"
    )
    exit()


RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"


helper_1 = Helper(CHAT, COOKIES, is_do_cleanup=False)
helper_2 = Helper(CHAT_2, None, is_do_cleanup=False)
read_aloud_queue = Queue()
is_playing_queue = Queue()
tts_lang = argv[-2]
tts_speed = argv[-1]
prompt = ""


def read_aloud_thread(lang, speed, semitones):
    while True:
        if read_aloud_queue.empty():
            sleep(0.5)
            continue

        content = read_aloud_queue.queue[0]

        if not isinstance(content, tuple) or len(content) != 2:
            continue

        response, response_id = read_aloud_queue.get()
        read_aloud(response, response_id, lang, speed, semitones)


def start_read_aloud_thread(target: Callable, args: tuple):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


def main():
    is_run = True
    response_id = 0
    initial_prompt = str(input("-> Initial prompt: "))
    start_read_aloud_thread(
        target=read_aloud_thread,
        args=(
            tts_lang,
            tts_speed,
            1,
        ),
    )
    start_read_aloud_thread(
        target=read_aloud_thread,
        args=(
            tts_lang,
            tts_speed,
            -2,
        ),
    )

    while is_run:
        try:
            response_1, response_id = handle_response(
                helper_1, initial_prompt, response_id, BLUE
            )
            read_aloud_queue.put((response_1, response_id))

            response_2, response_id = handle_response(
                helper_2, response_1, response_id, GREEN
            )
            read_aloud_queue.put((response_2, response_id))

            initial_prompt = response_2

        except KeyboardInterrupt:
            is_run = False

        except HelperException as h:
            print(h)

        except JavascriptException:
            print("JavascriptException")

        except Exception as e:
            print(str(e))


def handle_response(helper: Helper, prompt: str, response_id: int, color):
    response = helper.send_prompt(prompt)
    response = filter_response(response)
    response = ".".join(response.split(".")[:4])
    color_print(f"{response.strip()}\n", color)
    return response, response_id + 1


def filter_response(response: str) -> str:
    return (
        response.replace("ChatGPT said:", "")
        .replace("Memory updated", "")
        .replace("4o mini", "")
    )


def color_print(text, color):
    print(f"{color}{text}{RESET}")


def read_aloud(text: str, identifier: int, lang="en", speed=1.0, semitones=0):
    tts = gTTS(text=text or "Empty message", lang=lang, slow=False)
    filename = f"voice_{str(identifier)}.mp3"
    output_path = f"{TTS}/{filename}"
    tts.save(output_path)
    change_pitch(output_path, output_path, semitones)

    while not is_playing_queue.empty():
        sleep(0.5)
        pass

    os.system(
        f"ffmpeg -y -i {output_path} -b:a 64k -ar 16000 {output_path} > /dev/null 2>&1"
    )
    is_playing_queue.put("playing")
    os.system(f"mpv --speed={str(speed)} {output_path} > /dev/null 2>&1")
    is_playing_queue.get()
    os.system(f"rm {output_path}")


def change_pitch(input_file: str, output_file, semitones):
    audio = AudioSegment.from_file(input_file)
    new_sample_rate = int(audio.frame_rate * (2 ** (semitones / 12.0)))
    pitched_audio = audio._spawn(
        audio.raw_data, overrides={"frame_rate": new_sample_rate}
    )
    pitched_audio = pitched_audio.set_frame_rate(audio.frame_rate)
    pitched_audio.export(output_file, format="mp3")


if __name__ == "__main__":
    main()
