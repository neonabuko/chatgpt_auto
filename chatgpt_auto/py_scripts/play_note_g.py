# play_note_g.py
from mingus.midi import fluidsynth
import time

fluidsynth.init(r"/usr/share/mscore-4.3/sound/MS\ Basic.sf3")  # Path to a SoundFont file
volume = 0.5  # Volume (0.0 to 1.0)

fluidsynth.set_instrument(1, 0)
fluidsynth.play_Note(4)
time.sleep(0.5)
fluidsynth.stop_everything()
