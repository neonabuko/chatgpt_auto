# simple_gui.py
import tkinter as tk
from tkinter import messagebox

def on_button_click():
    messagebox.showinfo("Message", "Button clicked!")

# Create the main window
root = tk.Tk()
root.title("Simple GUI")
root.geometry("300x200")

# Create a button
button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=20)

# Run the application
root.mainloop()