# play_note_e.py
import pygame
import time

pygame.mixer.init()
frequency = 329.63  # Frequency of E note in Hz
duration = 0.5  # Duration in seconds
volume = 0.5  # Volume (0.0 to 1.0)

sound = pygame.mixer.Sound(frequency=frequency)
sound.set_volume(volume)
sound.play()
time.sleep(duration)
sound.stop()