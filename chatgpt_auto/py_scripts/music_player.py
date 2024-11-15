# music_player.py
import tkinter as tk
from tkinter import messagebox
import os
import pygame

class MusicPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Music Player")
        self.master.geometry("400x300")
        self.master.config(bg="#2C3E50")
        
        pygame.mixer.init()

        # Create listbox for songs
        self.song_listbox = tk.Listbox(master, bg="#34495E", fg="#ECF0F1", font=("Helvetica", 12), selectmode=tk.SINGLE)
        self.song_listbox.pack(pady=20, fill=tk.BOTH, expand=True)
        
        self.load_songs()

        # Play button
        self.play_button = tk.Button(master, text="Play", command=self.play_song, bg="#3498DB", fg="#ECF0F1", font=("Helvetica", 12))
        self.play_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Pause button
        self.pause_button = tk.Button(master, text="Pause", command=self.pause_song, bg="#F39C12", fg="#ECF0F1", font=("Helvetica", 12))
        self.pause_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Stop button
        self.stop_button = tk.Button(master, text="Stop", command=self.stop_song, bg="#E74C3C", fg="#ECF0F1", font=("Helvetica", 12))
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

    def load_songs(self):
        music_dir = '/home/neo/Music'
        try:
            songs = sorted([song for song in os.listdir(music_dir) if song.endswith('.mp3')])
            for song in songs:
                self.song_listbox.insert(tk.END, song)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def play_song(self):
        selected_song = self.song_listbox.curselection()
        if selected_song:
            song_name = self.song_listbox.get(selected_song)
            pygame.mixer.music.load(os.path.join('/home/neo/Music', song_name))
            pygame.mixer.music.play()

    def pause_song(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def stop_song(self):
        pygame.mixer.music.stop()

root = tk.Tk()
music_player = MusicPlayer(root)
root.mainloop()