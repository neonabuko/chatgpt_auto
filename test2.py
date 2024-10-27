import os
from gtts import gTTS
from constants import TTS


def read_aloud(text: str, identifier: int, lang="en"):
    tts = gTTS(text=text, lang=lang, slow=False)
    filename = f"voice_{str(identifier)}.mp3"
    output_path = f"{TTS}/{filename}"
    tts.save(output_path)
    os.system(f"mpv {output_path} > /dev/null 2>&1 && rm {output_path}")

print("Hey, what's up?")
read_aloud("Hey, what's up?", 0)