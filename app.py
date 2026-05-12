import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import requests
import cv2
from PIL import Image, ImageTk

VERSION_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/version.json"

DOWNLOADS = Path.home() / "Downloads"
if not DOWNLOADS.exists():
    DOWNLOADS = Path.home()

VIDEO_PATH = DOWNLOADS / "update.mp4"
TEMP_PATH = DOWNLOADS / "update.mp4.part"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Updater")
        self.root.geometry("1000x700")
        self.root.configure(bg="#111111")

        self.cap = None
        self.playing = False

        self.status = tk.StringVar(value="Preparat")
        self.percent = tk.StringVar(value="0%")

        self._build_ui()

    def _build_ui(self):
        title = tk.Label(
            self.root,
            text="Sistema d'Actualització",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#111111"
        )
        title.pack(pady=10)

        controls = tk.Frame(self.root, bg="#111111")
        controls.pack()

        self.download_btn = tk.Button(
            controls,
            text="Descarregar vídeo",
            command=self.start_download,
            font=("Arial", 12, "bold"),
            bg="#00aa44",
            fg="white",
            width=22,
            height=2
        )
        self.download_btn.grid(row=0, column=0, padx=8)

        self.play_btn = tk.Button(
            controls,
            text="Reproduir",
            command=self.play_video,
            font=("Arial", 12, "bold"),
            bg="#2266dd",
            fg="white",
            width=15,
            height=2
        )
        self.play_btn.grid(row=0, column=1, padx=8)

        self.stop_btn = tk.Button(
            controls,
            text="Aturar",
            command=self.stop_video,
            font=("Arial", 12, "bold"),
            bg="#cc3333",
            fg="white",
            width=12,
            height=2
        )
        self.stop_btn.grid(row=0, column=2, padx=8)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=500,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(pady=15)

        percent_label = tk.Label(
            self.root,
            textvariable=self.percent,
            font=("Arial", 11),
            fg="white",
            bg="#111111"
        )
        percent_label.pack()

        status_label = tk.Label(
            self.root,
            textvariable=self.status,
            font=("Arial", 11),
            fg="#cccccc",
            bg="#111111"
        )
        status_label.pack(pady=5)

        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(pady=20, fill="both", expand=True)

    def set_status(self, text):
        self.status.set(text)
        self.root.update_idletasks()

    def set_progress(self, value):
        self.progress["value"] = value
        self.percent.set(f"{value}%")
        self.root.update_idletasks()

    def start_download(self):
        self.download_btn.config(state="disabled")
        self.set_progress(0)
        self.set_status("Llegint JSON...")
        threading.Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        try:
            r = requests.get(VERSION_URL, timeout=20)
            r.raise_for_status()
            data = r.json()

            video_url = data.get("video_url")
            if not video_url:
                raise ValueError("El JSON no té camp 'video_url'.")

            self.root.after(0, lambda: self.set_status("Descarregant vídeo..."))

            with requests.get(video_url, stream=True, timeout=30) as resp:
                resp.raise_for_status()

                content_type = resp.headers.get("content-type", "")
                total = int(resp.headers.get("content-length", 0))
                downloaded = 0

                with open(TEMP_PATH, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            if total > 0:
                                percent = int(downloaded * 100 / total)
                                self.root.after(0, lambda p=percent: self.set_progress(p))

            if not TEMP_PATH.exists() or TEMP_PATH.stat().st_size < 1024:
                raise ValueError("El fitxer descarregat és massa petit. Segurament no és un vídeo real.")

            # Comprovació simple de MP4: bytes 4:8 solen ser b'ftyp'
            with open(TEMP_PATH, "rb") as f:
                header = f.read(16)

            if len(header) < 8 or header[4:8] != b"ftyp":
                preview = header[:16].hex(" ")
                raise ValueError(
                    "El fitxer descarregat no sembla un MP4 vàlid.\n"
                    f"Content-Type: {content_type}\n"
                    f"Header: {preview}\n"
                    "Probablement el link és incorrecte o GitHub està retornant HTML/text."
                )

            if VIDEO_PATH.exists():
                try:
                    VIDEO_PATH.unlink()
                except PermissionError:
                    raise PermissionError(f"No puc substituir el fitxer perquè està obert: {VIDEO_PATH}")

            os.replace(TEMP_PATH, VIDEO_PATH)

            self.root.after(0, lambda: self.set_status("Descàrrega completada. Reproduint..."))
            self.root.after(0, lambda: self.set_progress(100))
            self.root.after(0, self.play_video)

        except Exception as e:
            try:
                if TEMP_PATH.exists():
                    TEMP_PATH.unlink()
            except Exception:
                pass

            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_status("Error en la descàrrega."))

        finally:
            self.root.after(0, lambda: self.download_btn.config(state="normal"))

    def play_video(self):
        if not VIDEO_PATH.exists():
            messagebox.showwarning("Atenció", "No hi ha cap vídeo descarregat.")
            return

        self.stop_video()

        try:
            self.cap = cv2.VideoCapture(str(VIDEO_PATH))

            if not self.cap.isOpened():
                raise ValueError("OpenCV no pot obrir el vídeo. El fitxer està corrupte o no és un MP4 vàlid.")

            self.playing = True
            self.set_status("Reproduint vídeo dins la finestra...")
            self.update_frame()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_video(self):
        self.playing = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def update_frame(self):
        if not self.playing or self.cap is None:
            return

        ret, frame = self.cap.read()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, _ = frame.shape
            max_w = 900
            max_h = 500
            scale = min(max_w / w, max_h / h)
            nw = max(1, int(w * scale))
            nh = max(1, int(h * scale))

            frame = cv2.resize(frame, (nw, nh))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk

            fps = self.cap.get(cv2.CAP_PROP_FPS)
            delay = int(1000 / fps) if fps and fps > 1 else 33
            self.root.after(delay, self.update_frame)

        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.root.after(1, self.update_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
