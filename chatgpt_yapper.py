import multiprocessing
import os
import re
from time import sleep
from gtts import gTTS
from constants import TTS
from chatgpt_auto import ChatGPTAuto
from test_constants import BLUE, GREEN, RESET
from pydub import AudioSegment


class ChatGPTYapper:
    """Manager with helper methods for tests."""
    def __init__(self) -> None:
        self.queue = multiprocessing.Manager().Queue()
        self.stop = multiprocessing.Event()
        self.is_reading_aloud = False

    
    def _break_down(self, text: str) -> list[str]:
        """Breaks text down into sentences by considering '.', '?' and ':' as sentence finishers."""
        sentences = re.split(r"(?<=[?.:])\s*", text)
        return [s.lstrip() for s in sentences if s.strip()]

    
    def _filter_response(self, response: str, max_sentences: int) -> str:
        """Reduces response to maximum n of incidences of '.', '?' or ':' and removes known ChatGPT response labels."""
        delimiters = r"[?.:]"
        matches = re.finditer(delimiters, response)
        count = 0
        cut_off_index = len(response)

        for match in matches:
            count += 1
            if count >= max_sentences:
                cut_off_index = match.start() + 1
                break

        response = response[:cut_off_index]
        return (
            response.replace("ChatGPT said:", "")
            .replace("Memory updated", "")
            .replace("4o mini", "")
            .replace("Copy code", "")
            .strip()
        )

    
    def color_print(self, text, color) -> None:
        print(f"{color}{text}{RESET}")

    
    def _generate_tts(self, text: str, lang: str, audio_id: str, pitch=0) -> None:
        """Generates Text-To-Speech, changes pitch, then saves with lower quality."""
        tts = gTTS(text=text or "Empty message", lang=lang, slow=False)
        filename = f"voice_{audio_id}.mp3"
        output_path = f"{TTS}/{filename}"
        tts.save(output_path)
        self._change_pitch(output_path, output_path, pitch)
        os.system(
            f"ffmpeg -y -i {output_path} -b:a 64k -ar 16000 {output_path} > /dev/null 2>&1"
        )

    
    def _start_gen_tts(self, sentences: list, pitch_change=0) -> None:
        """Starts 1 generate_tts() process per sentence in response."""
        processes = []
        for audio_id, sentence in enumerate(sentences):
            p = multiprocessing.Process(
                target=self._generate_tts, args=(sentence, "en", audio_id, pitch_change)
            )
            p.name = "Generate TTS Process"
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    
    def _read_aloud(self, speed=1.0) -> None:
        """Reads each generated tts present in TTS folder in alphanumeric order."""
        audios = [audio.path for audio in os.scandir(TTS)]
        audios = sorted(audios)

        for audio in audios:
            os.system(f"mpv --speed={str(speed)} {audio} > /dev/null 2>&1")
            if os.path.exists(audio):
                os.system(f"rm {audio}")

    
    def _change_pitch(
        self, input_file: str, output_file: str, semitones: int | float
    ) -> None:
        """Changes pitch to characterize different voices talking. Useful when having multiple instances of ChatGPT talking to each other."""
        audio = AudioSegment.from_file(input_file)
        new_sample_rate = int(audio.frame_rate * (2 ** (semitones / 12.0)))
        pitched_audio = audio._spawn(
            audio.raw_data, overrides={"frame_rate": new_sample_rate}
        )
        pitched_audio = pitched_audio.set_frame_rate(audio.frame_rate)
        pitched_audio.export(output_file, format="mp3")

    
    def _handle_conversation(
        self, chat_1: ChatGPTAuto, chat_2: ChatGPTAuto, initial_prompt: str
    ) -> None:
        """Handles flow of conversation between 2 instances.
        Sends prompt to one instance, gets response, adds it to queue for later use by other processes,
        repeats with the other instance.
        """
        current_chat = chat_1
        color = BLUE
        while not self.stop.is_set():
            try:
                response = current_chat.send(initial_prompt)
                f_response = self._filter_response(response, max_sentences=5)
                sentences = self._break_down(f_response)
                self.queue.put(sentences)

                initial_prompt = f_response

                self.color_print(f"{f_response}\n", color)

                if current_chat == chat_1:
                    current_chat = chat_2
                    color = GREEN
                else:
                    current_chat = chat_1
                    color = BLUE
            except:
                continue

    
    def _handle_read_aloud(self) -> None:
        """Process that constantly looks for responses in queue. If finds one, generates its tts files then reads them aloud."""
        pitch_change = 2
        while not self.stop.is_set():
            try:
                response = self.queue.get(timeout=1)
            except:
                continue
            if response is not None:
                self._start_gen_tts(sentences=response, pitch_change=pitch_change)

                while self.is_reading_aloud:
                    sleep(0.3)
                    pass
                self.is_reading_aloud = True
                self._read_aloud(speed=1.8)
                self.is_reading_aloud = False

                pitch_change = 2 if pitch_change == -2 else -2

    
    def start_conversation_process(
        self, chat_1: ChatGPTAuto, chat_2: ChatGPTAuto, initial_prompt: str
    ) -> multiprocessing.Process:
        conversation = multiprocessing.Process(
            target=self._handle_conversation,
            args=(
                chat_1,
                chat_2,
                initial_prompt,
            ),
        )
        conversation.daemon = True
        conversation.name = "Conversation Process"
        conversation.start()

        reading = multiprocessing.Process(target=self._handle_read_aloud)
        reading.name = "Read Aloud Process"
        reading.start()

        return conversation
