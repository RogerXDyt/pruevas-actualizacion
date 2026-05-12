import tkinter as tk
from tkinter import messagebox
import requests
import os

# LINK DEL JSON
VERSION_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/version.json"

# NOM DEL VIDEO DESCARREGAT
VIDEO_FILE = "update.mp4"


def descarregar_actualizacio():
    try:
        # DESCARREGAR JSON
        resposta = requests.get(VERSION_URL)
        resposta.raise_for_status()

        dades = resposta.json()

        # OBTENIR URL DEL VIDEO
        video_url = dades["video_url"]
        versio = dades["version"]

        # DESCARREGAR VIDEO
        video = requests.get(video_url, stream=True)
        video.raise_for_status()

        total = int(video.headers.get('content-length', 0))
        descarregat = 0

        with open(VIDEO_FILE, "wb") as f:
            for chunk in video.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    descarregat += len(chunk)

                    if total > 0:
                        percent = int((descarregat / total) * 100)
                        barra["value"] = percent
                        text_percent.config(text=f"{percent}%")
                        root.update_idletasks()

        messagebox.showinfo(
            "Actualitzat",
            f"Video descarregat correctament!\nVersio: {versio}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# FINESTRA
root = tk.Tk()
root.title("Sistema d'Actualizacions")
root.geometry("420x250")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

# TITOL
titol = tk.Label(
    root,
    text="Actualizador de Videos",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#1e1e1e"
)
titol.pack(pady=20)

# BOTO
boto = tk.Button(
    root,
    text="Descarregar Actualizacio",
    font=("Arial", 12, "bold"),
    bg="#00aa44",
    fg="white",
    width=25,
    height=2,
    command=descarregar_actualizacio
)
boto.pack(pady=10)

# BARRA
barra = tk.ttk.Progressbar(
    root,
    orient="horizontal",
    length=300,
    mode="determinate"
)
barra.pack(pady=15)

# PERCENTATGE
text_percent = tk.Label(
    root,
    text="0%",
    font=("Arial", 12),
    fg="white",
    bg="#1e1e1e"
)
text_percent.pack()

# INFO
info = tk.Label(
    root,
    text="GitHub Auto Update System",
    font=("Arial", 10),
    fg="#aaaaaa",
    bg="#1e1e1e"
)
info.pack(side="bottom", pady=10)

# IMPORT ttk
from tkinter import ttk

root.mainloop()
