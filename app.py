import os
import platform
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import requests
import vlc

# JSON de GitHub RAW
VERSION_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/version.json"

# Carpeta segura
DOWNLOADS_DIR = Path.home() / "Downloads"
if not DOWNLOADS_DIR.exists():
    DOWNLOADS_DIR = Path.home()

FINAL_VIDEO = DOWNLOADS_DIR / "update.mp4"
TEMP_VIDEO = DOWNLOADS_DIR / "update.mp4.part"


class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Actualitzador de vídeo")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e1e")

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.status_var = tk.StringVar(value="Preparat.")
        self.percent_var = tk.StringVar(value="0%")
        self.is_playing = False

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        title = tk.Label(
            self.root,
            text="Sistema d'Actualització",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        title.pack(pady=(14, 6))

        subtitle = tk.Label(
            self.root,
            text="Descarrega el vídeo des de GitHub i reprodueix-lo dins l'app",
            font=("Arial", 10),
            fg="#b0b0b0",
            bg="#1e1e1e"
        )
        subtitle.pack(pady=(0, 10))

        controls = tk.Frame(self.root, bg="#1e1e1e")
        controls.pack(pady=6)

        self.download_btn = tk.Button(
            controls,
            text="Descarregar i reproduir",
            command=self.start_download,
            font=("Arial", 12, "bold"),
            bg="#00aa44",
            fg="white",
            activebackground="#008833",
            activeforeground="white",
            width=24,
            height=2,
            relief="flat"
        )
        self.download_btn.grid(row=0, column=0, padx=8)

        self.play_btn = tk.Button(
            controls,
            text="Reproduir vídeo",
            command=self.play_video,
            font=("Arial", 12, "bold"),
            bg="#2d6cdf",
            fg="white",
            activebackground="#1e54b8",
            activeforeground="white",
            width=18,
            height=2,
            relief="flat"
        )
        self.play_btn.grid(row=0, column=1, padx=8)

        self.stop_btn = tk.Button(
            controls,
            text="Aturar",
            command=self.stop_video,
            font=("Arial", 12, "bold"),
            bg="#cc3333",
            fg="white",
            activebackground="#a82828",
            activeforeground="white",
            width=12,
            height=2,
            relief="flat"
        )
        self.stop_btn.grid(row=0, column=2, padx=8)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=520,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(pady=(12, 4))

        percent_label = tk.Label(
            self.root,
            textvariable=self.percent_var,
            font=("Arial", 11),
            fg="white",
            bg="#1e1e1e"
        )
        percent_label.pack()

        status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 10),
            fg="#d0d0d0",
            bg="#1e1e1e"
        )
        status_label.pack(pady=(6, 10))

        # Marc del vídeo
        video_container = tk.Frame(self.root, bg="black", width=860, height=420)
        video_container.pack(pady=8)
        video_container.pack_propagate(False)

        self.video_panel = tk.Frame(video_container, bg="black", width=860, height=420)
        self.video_panel.pack(fill="both", expand=True)

        self.root.update_idletasks()
        self._set_player_handle()

    def _set_player_handle(self):
        handle = self.video_panel.winfo_id()
        system = platform.system()

        if system == "Windows":
            self.player.set_hwnd(handle)
        elif system == "Linux":
            self.player.set_xwindow(handle)
        elif system == "Darwin":
            self.player.set_nsobject(handle)

    def set_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()

    def set_progress(self, value):
        self.progress["value"] = value
        self.percent_var.set(f"{value}%")
        self.root.update_idletasks()

    def start_download(self):
        self.download_btn.config(state="disabled")
        self.set_progress(0)
        self.set_status("Comprovant actualització...")
        threading.Thread(target=self.download_update, daemon=True).start()

    def download_update(self):
        try:
            r = requests.get(VERSION_URL, timeout=20)
            r.raise_for_status()
            data = r.json()

            video_url = data.get("video_url")
            version = data.get("version", "desconeguda")

            if not video_url:
                raise ValueError("El JSON no conté 'video_url'.")

            self.root.after(0, lambda: self.set_status(f"Descarregant versió {version}..."))

            with requests.get(video_url, stream=True, timeout=30) as resp:
                resp.raise_for_status()

                total = int(resp.headers.get("content-length", 0))
                downloaded = 0

                with open(TEMP_VIDEO, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            if total > 0:
                                percent = int((downloaded / total) * 100)
                                self.root.after(0, lambda p=percent: self.set_progress(p))

            if FINAL_VIDEO.exists():
                try:
                    FINAL_VIDEO.unlink()
                except PermissionError:
                    raise PermissionError(f"No puc substituir el fitxer perquè està obert: {FINAL_VIDEO}")

            os.replace(TEMP_VIDEO, FINAL_VIDEO)

            self.root.after(0, lambda: self.set_status("Descàrrega completada. Reproduint..."))
            self.root.after(0, self.play_video)
            self.root.after(0, lambda: self.set_progress(100))

        except Exception as e:
            try:
                if TEMP_VIDEO.exists():
                    TEMP_VIDEO.unlink()
            except Exception:
                pass

            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_status("Error en la descàrrega."))

        finally:
            self.root.after(0, lambda: self.download_btn.config(state="normal"))

    def play_video(self):
        if not FINAL_VIDEO.exists():
            messagebox.showwarning("Atenció", "Encara no hi ha cap vídeo descarregat.")
            return

        try:
            self.stop_video()

            self._set_player_handle()
            media = self.instance.media_new(str(FINAL_VIDEO))
            self.player.set_media(media)
            self.player.play()
            self.is_playing = True
            self.set_status("Reproduint vídeo dins la finestra...")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_video(self):
        try:
            if self.player:
                self.player.stop()
            self.is_playing = False
        except Exception:
            pass

    def on_close(self):
        self.stop_video()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()
