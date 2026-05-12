import os
import shutil
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import requests
import cv2
from PIL import Image, ImageTk

VERSION_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/version.json"

BASE_DIR = Path.home() / "Downloads"
if not BASE_DIR.exists():
    BASE_DIR = Path.home()

TEMP_MP4 = BASE_DIR / "update_raw.mp4"
FIXED_MP4 = BASE_DIR / "update_fixed.mp4"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Updater")
        self.root.geometry("1000x720")
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
        controls.pack(pady=5)

        self.download_btn = tk.Button(
            controls,
            text="Descarregar i reproduir",
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
            width=14,
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
            length=560,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(pady=15)

        tk.Label(
            self.root,
            textvariable=self.percent,
            font=("Arial", 11),
            fg="white",
            bg="#111111"
        ).pack()

        tk.Label(
            self.root,
            textvariable=self.status,
            font=("Arial", 11),
            fg="#cccccc",
            bg="#111111"
        ).pack(pady=5)

        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(pady=18, fill="both", expand=True)

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
        threading.Thread(target=self.download_and_play, daemon=True).start()

    def download_and_play(self):
        try:
            r = requests.get(VERSION_URL, timeout=20)
            r.raise_for_status()
            data = r.json()

            video_url = data.get("video_url")
            if not video_url:
                raise ValueError("El JSON no conté el camp 'video_url'.")

            self.root.after(0, lambda: self.set_status("Descarregant vídeo..."))

            with requests.get(video_url, stream=True, timeout=40) as resp:
                resp.raise_for_status()

                total = int(resp.headers.get("content-length", 0))
                downloaded = 0

                with open(TEMP_MP4, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1024 * 128):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                p = int(downloaded * 100 / total)
                                self.root.after(0, lambda v=p: self.set_progress(v))

            if not TEMP_MP4.exists() or TEMP_MP4.stat().st_size < 1024:
                raise ValueError("El fitxer descarregat és massa petit.")

            ffmpeg = shutil.which("ffmpeg")
            if not ffmpeg:
                raise RuntimeError("No trobo ffmpeg al PATH. Instal·la'l i reinicia la consola.")

            self.root.after(0, lambda: self.set_status("Remuxant el vídeo amb ffmpeg..."))

            if FIXED_MP4.exists():
                try:
                    FIXED_MP4.unlink()
                except PermissionError:
                    pass

            cmd = [
                ffmpeg,
                "-y",
                "-i", str(TEMP_MP4),
                "-c", "copy",
                "-movflags", "+faststart",
                str(FIXED_MP4)
            ]

            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(
                    "ffmpeg ha fallat al remux.\n\n"
                    f"STDERR:\n{proc.stderr}"
                )

            if not FIXED_MP4.exists() or FIXED_MP4.stat().st_size < 1024:
                raise ValueError("El vídeo remuxat no s'ha creat bé.")

            self.root.after(0, lambda: self.set_progress(100))
            self.root.after(0, lambda: self.set_status("Reproduint..."))
            self.root.after(0, self.play_video)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_status("Error"))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state="normal"))

    def play_video(self):
        if not FIXED_MP4.exists():
            messagebox.showwarning("Atenció", "No hi ha cap vídeo preparat.")
            return

        self.stop_video()

        self.cap = cv2.VideoCapture(str(FIXED_MP4))
        if not self.cap.isOpened():
            messagebox.showerror("Error", "OpenCV no pot obrir el vídeo remuxat.")
            return

        self.playing = True
        self.update_frame()

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
            max_w, max_h = 920, 520
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
