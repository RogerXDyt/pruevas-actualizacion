import tkinter as tk
from tkinter import messagebox, ttk
import requests

# JSON DE GITHUB
VERSION_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/version.json"

# NOM DEL VIDEO
VIDEO_FILE = "update.mp4"


def descarregar_actualizacio():
    try:
        # DESCARREGAR JSON
        resposta = requests.get(VERSION_URL)
        resposta.raise_for_status()

        dades = resposta.json()

        video_url = dades["video_url"]
        versio = dades["version"]

        # DESCARREGAR VIDEO
        video = requests.get(video_url, stream=True)
        video.raise_for_status()

        total = int(video.headers.get("content-length", 0))
        descarregat = 0

        with open(VIDEO_FILE, "wb") as f:
            for chunk in video.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    descarregat += len(chunk)

                    if total > 0:
                        percent = int((descarregat / total) * 100)
                        barra["value"] = percent
                        percentatge.config(text=f"{percent}%")
                        root.update_idletasks()

        messagebox.showinfo(
            "Correcte",
            f"Video descarregat!\nVersio: {versio}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# FINESTRA
root = tk.Tk()
root.title("Actualizador")
root.geometry("400x250")
root.configure(bg="#1e1e1e")

# TITOL
titol = tk.Label(
    root,
    text="Sistema d'Actualizacions",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#1e1e1e"
)
titol.pack(pady=20)

# BOTO
boto = tk.Button(
    root,
    text="Descarregar Video",
    command=descarregar_actualizacio,
    font=("Arial", 12, "bold"),
    bg="#00aa44",
    fg="white",
    width=25,
    height=2
)
boto.pack(pady=10)

# BARRA
barra = ttk.Progressbar(
    root,
    orient="horizontal",
    length=300,
    mode="determinate"
)
barra.pack(pady=15)

# TEXT %
percentatge = tk.Label(
    root,
    text="0%",
    font=("Arial", 12),
    fg="white",
    bg="#1e1e1e"
)
percentatge.pack()

root.mainloop()
