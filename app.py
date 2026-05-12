import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import requests
import cv2
from PIL import Image, ImageTk

# JSON
VERSION_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/version.json"

# Carpeta segura
DOWNLOADS = Path.home() / "Downloads"

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

        self.crear_ui()

    def crear_ui(self):

        title = tk.Label(
            self.root,
            text="Sistema d'Actualitzacio",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#111111"
        )
        title.pack(pady=10)

        controls = tk.Frame(self.root, bg="#111111")
        controls.pack()

        self.download_btn = tk.Button(
            controls,
            text="Descarregar Video",
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
            text="Stop",
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

        # VIDEO PANEL
        self.video_label = tk.Label(
            self.root,
            bg="black"
        )
        self.video_label.pack(
            pady=20,
            fill="both",
            expand=True
        )

    def set_status(self, text):
        self.status.set(text)
        self.root.update_idletasks()

    def set_progress(self, value):
        self.progress["value"] = value
        self.percent.set(f"{value}%")
        self.root.update_idletasks()

    def start_download(self):
        threading.Thread(
            target=self.download_video,
            daemon=True
        ).start()

    def download_video(self):

        try:

            self.set_status("Llegint JSON...")

            r = requests.get(VERSION_URL)
            data = r.json()

            video_url = data["video_url"]

            self.set_status("Descarregant video...")

            response = requests.get(
                video_url,
                stream=True
            )

            total = int(
                response.headers.get(
                    "content-length",
                    0
                )
            )

            downloaded = 0

            with open(TEMP_PATH, "wb") as f:

                for chunk in response.iter_content(65536):

                    if chunk:

                        f.write(chunk)

                        downloaded += len(chunk)

                        if total > 0:

                            percent = int(
                                downloaded / total * 100
                            )

                            self.set_progress(percent)

            if VIDEO_PATH.exists():
                try:
                    VIDEO_PATH.unlink()
                except:
                    pass

            os.replace(TEMP_PATH, VIDEO_PATH)

            self.set_status("Video descarregat!")

            self.play_video()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    def play_video(self):

        if not VIDEO_PATH.exists():

            messagebox.showwarning(
                "Error",
                "No existeix el video"
            )

            return

        self.stop_video()

        self.cap = cv2.VideoCapture(
            str(VIDEO_PATH)
        )

        self.playing = True

        self.update_frame()

    def stop_video(self):

        self.playing = False

        if self.cap:
            self.cap.release()
            self.cap = None

    def update_frame(self):

        if not self.playing:
            return

        ret, frame = self.cap.read()

        if ret:

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            # REDIMENSIONAR
            h, w, _ = frame.shape

            max_w = 900
            max_h = 500

            scale = min(
                max_w / w,
                max_h / h
            )

            nw = int(w * scale)
            nh = int(h * scale)

            frame = cv2.resize(
                frame,
                (nw, nh)
            )

            img = Image.fromarray(frame)

            imgtk = ImageTk.PhotoImage(
                image=img
            )

            self.video_label.imgtk = imgtk

            self.video_label.configure(
                image=imgtk
            )

            self.root.after(
                15,
                self.update_frame
            )

        else:

            # LOOP
            self.cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                0
            )

            self.root.after(
                15,
                self.update_frame
            )


root = tk.Tk()

app = App(root)

root.mainloop()
