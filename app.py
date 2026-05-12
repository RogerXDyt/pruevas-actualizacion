import tkinter as tk
from tkinter import messagebox
import requests
import os

VERSION_URL = "https://raw.githubusercontent.com/TUUSUARIO/video-updates/main/version.json"

def descarregar_video():
    try:
        resposta = requests.get(VERSION_URL)
        dades = resposta.json()

        video_url = dades["video_url"]

        video = requests.get(video_url)

        with open("video_actualitzat.mp4", "wb") as f:
            f.write(video.content)

        messagebox.showinfo("Correcte", "Video descarregat!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Actualitzador Video")
root.geometry("300x200")

boto = tk.Button(
    root,
    text="Descarregar actualitzacio",
    command=descarregar_video,
    height=3,
    width=25
)

boto.pack(expand=True)

root.mainloop()
