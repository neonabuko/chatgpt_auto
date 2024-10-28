import multiprocessing
import os
import re
import threading
from typing import Callable
from gtts import gTTS
from constants import TTS
from test_constants import RESET
from pydub import AudioSegment


class Manager:
    """Manager with helper functions for tests"""
    def __init__(self) -> None:
        self.queue = multiprocessing.Manager().Queue()
        self.stop = multiprocessing.Event()
        self.is_reading_aloud = False
    
    def start_thread(self, target: Callable, args: tuple) -> None:
        t = threading.Thread(target=target, args=args)
        t.daemon = True
        t.start()


    def break_down(self, text: str) -> list:
        sentences = re.split(r'(?<=[?.])\s*', text)
        return [s.lstrip() for s in sentences if s.strip()]     


    def filter_response(self, response: str) -> str:
        return (
            response.replace("ChatGPT said:", "")
            .replace("Memory updated", "")
            .replace("4o mini", "")
            .replace("Copy code", "")
        )

    
    def color_print(self, text, color) -> None:
        print(f"{color}{text}{RESET}")

    
    def generate_tts(self, text: str, lang: str, audio_id: str, pitch=0):
        tts = gTTS(text=text or "Empty message", lang=lang, slow=False)
        filename = f"voice_{audio_id}.mp3"
        output_path = f"{TTS}/{filename}"
        tts.save(output_path)
        self.change_pitch(output_path, output_path, pitch)
        os.system(
            f"ffmpeg -y -i {output_path} -b:a 64k -ar 16000 {output_path} > /dev/null 2>&1"
        )


    def start_gen_tts(self, sentences: list, pitch_change=0) -> None:
        processes = []
        for audio_id, sentence in enumerate(sentences):
            p = multiprocessing.Process(target=self.generate_tts, args=(sentence, 'en', audio_id, pitch_change))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()   


    def read_aloud(self, speed=1.0) -> None:
        audios = [audio.path for audio in os.scandir(TTS)]
        audios = sorted(audios)

        for audio in audios:
            os.system(f"mpv --speed={str(speed)} {audio} > /dev/null 2>&1")
            if os.path.exists(audio):
                os.system(f"rm {audio}")


    def change_pitch(self, input_file: str, output_file, semitones):
        audio = AudioSegment.from_file(input_file)
        new_sample_rate = int(audio.frame_rate * (2 ** (semitones / 12.0)))
        pitched_audio = audio._spawn(
            audio.raw_data, overrides={"frame_rate": new_sample_rate}
        )
        pitched_audio = pitched_audio.set_frame_rate(audio.frame_rate)
        pitched_audio.export(output_file, format="mp3")