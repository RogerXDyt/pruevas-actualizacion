import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import requests

# JSON de GitHub RAW
VERSION_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/version.json"

# Carpeta segura d'escriptura
DOWNLOADS_DIR = Path.home() / "Downloads"
if not DOWNLOADS_DIR.exists():
    DOWNLOADS_DIR = Path.home()

FINAL_VIDEO = DOWNLOADS_DIR / "update.mp4"
TEMP_VIDEO = DOWNLOADS_DIR / "update.mp4.part"


def ui_status(text: str) -> None:
    status_var.set(text)
    root.update_idletasks()


def ui_progress(value: int) -> None:
    progress["value"] = value
    percent_var.set(f"{value}%")
    root.update_idletasks()


def baixar_actualitzacio() -> None:
    boto.config(state="disabled")
    ui_progress(0)
    ui_status("Comprovant actualització...")

    try:
        # Llegir JSON
        r = requests.get(VERSION_URL, timeout=20)
        r.raise_for_status()
        dades = r.json()

        video_url = dades.get("video_url")
        versio = dades.get("version", "desconeguda")

        if not video_url:
            raise ValueError("El JSON no conté 'video_url'.")

        ui_status(f"Descarregant versió {versio}...")

        # Descarregar vídeo
        with requests.get(video_url, stream=True, timeout=30) as resp:
            resp.raise_for_status()

            total = int(resp.headers.get("content-length", 0))
            descarregat = 0

            with open(TEMP_VIDEO, "wb") as f:
                for chunk in resp.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        f.write(chunk)
                        descarregat += len(chunk)

                        if total > 0:
                            percent = int((descarregat / total) * 100)
                            ui_progress(percent)

        # Reemplaçar l'antic si existeix
        if FINAL_VIDEO.exists():
            try:
                FINAL_VIDEO.unlink()
            except PermissionError:
                raise PermissionError(
                    f"No puc substituir el fitxer perquè està obert: {FINAL_VIDEO}"
                )

        os.replace(TEMP_VIDEO, FINAL_VIDEO)

        ui_progress(100)
        ui_status("Descarrega completada.")
        messagebox.showinfo(
            "Correcte",
            f"Vídeo descarregat correctament.\n\nDesat a:\n{FINAL_VIDEO}"
        )

    except Exception as e:
        # Neteja el temporal si ha fallat
        try:
            if TEMP_VIDEO.exists():
                TEMP_VIDEO.unlink()
        except Exception:
            pass

        ui_status("Error en la descàrrega.")
        messagebox.showerror("Error", str(e))

    finally:
        boto.config(state="normal")


def iniciar_descarga() -> None:
    threading.Thread(target=baixar_actualitzacio, daemon=True).start()


root = tk.Tk()
root.title("Actualitzador de vídeo")
root.geometry("460x240")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

status_var = tk.StringVar(value="Preparat.")
percent_var = tk.StringVar(value="0%")

titol = tk.Label(
    root,
    text="Sistema d'Actualització",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#1e1e1e"
)
titol.pack(pady=(18, 8))

subtitol = tk.Label(
    root,
    text="Descarrega el vídeo d'actualització des de GitHub",
    font=("Arial", 10),
    fg="#b0b0b0",
    bg="#1e1e1e"
)
subtitol.pack(pady=(0, 14))

boto = tk.Button(
    root,
    text="Descarregar actualització",
    command=iniciar_descarga,
    font=("Arial", 12, "bold"),
    bg="#00aa44",
    fg="white",
    activebackground="#008833",
    activeforeground="white",
    width=24,
    height=2,
    relief="flat"
)
boto.pack(pady=6)

progress = ttk.Progressbar(
    root,
    orient="horizontal",
    length=340,
    mode="determinate",
    maximum=100
)
progress.pack(pady=(14, 6))

percent_label = tk.Label(
    root,
    textvariable=percent_var,
    font=("Arial", 11),
    fg="white",
    bg="#1e1e1e"
)
percent_label.pack()

status_label = tk.Label(
    root,
    textvariable=status_var,
    font=("Arial", 10),
    fg="#d0d0d0",
    bg="#1e1e1e"
)
status_label.pack(pady=(10, 0))

root.mainloop()
