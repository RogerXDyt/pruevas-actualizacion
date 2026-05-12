import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import time
import requests

UPDATE_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/update.txt"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Update Viewer")
        self.root.geometry("900x600")
        self.root.configure(bg="#0f1115")

        self.request_id = 0

        self.status = tk.StringVar(value="Preparat")
        self.percent = tk.StringVar(value="0%")

        self.build_ui()

    def build_ui(self):
        tk.Label(
            self.root,
            text="SYSTEM UPDATE",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#0f1115"
        ).pack(pady=10)

        self.btn = tk.Button(
            self.root,
            text="Carregar última versió",
            command=self.start,
            bg="#1f8fff",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=18,
            pady=10
        )
        self.btn.pack()

        self.progress = ttk.Progressbar(self.root, length=350, maximum=100)
        self.progress.pack(pady=10)

        tk.Label(self.root, textvariable=self.status,
                 fg="#c8d0dc", bg="#0f1115").pack()

        self.text = ScrolledText(
            self.root,
            bg="#12161d",
            fg="white",
            font=("Consolas", 11),
            wrap="word"
        )
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

    def start(self):
        self.request_id += 1
        rid = self.request_id

        self.btn.config(state="disabled")
        self.text.delete("1.0", "end")  # 🔥 importantíssim

        threading.Thread(target=self.load, args=(rid,), daemon=True).start()

    def load(self, rid):
        try:
            self.root.after(0, lambda: self.status.set("Descarregant..."))

            # 🔥 FORÇA REAL CACHE BUSTING (CLAVE)
            url = UPDATE_URL + f"?nocache={time.time_ns()}"

            headers = {
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "User-Agent": "Mozilla/5.0"
            }

            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()

            # si ja hi ha una altra petició nova, ignora aquesta
            if rid != self.request_id:
                return

            text = r.text

            # 🔥 doble assegurança: si arriba buit o igual, igual es reemplaça
            self.root.after(0, lambda: self.render(text))

            self.root.after(0, lambda: self.status.set("Actualitzat"))
            self.root.after(0, lambda: self.progress.configure(value=100))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        finally:
            self.root.after(0, lambda: self.btn.config(state="normal"))

    def render(self, text):
        # 🔥 neteja absoluta abans de mostrar res
        self.text.delete("1.0", "end")
        self.text.insert("end", text.strip())


root = tk.Tk()
App(root)
root.mainloop()
