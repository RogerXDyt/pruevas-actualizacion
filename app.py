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

        self.status = tk.StringVar(value="Preparat")
        self.percent = tk.StringVar(value="0%")

        self.request_id = 0  # 👈 clau per evitar duplicats

        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.root, bg="#0f1115")
        top.pack(fill="x", pady=10)

        tk.Label(top, text="SYSTEM UPDATE",
                 font=("Segoe UI", 20, "bold"),
                 fg="white", bg="#0f1115").pack()

        buttons = tk.Frame(self.root, bg="#0f1115")
        buttons.pack(pady=10)

        self.btn = tk.Button(
            buttons,
            text="Carregar última versió",
            command=self.start,
            bg="#1f8fff",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=18, pady=10
        )
        self.btn.grid(row=0, column=0, padx=8)

        self.progress = ttk.Progressbar(
            buttons, length=300, mode="determinate", maximum=100
        )
        self.progress.grid(row=0, column=1, padx=8)

        tk.Label(
            self.root,
            textvariable=self.status,
            fg="#c8d0dc",
            bg="#0f1115"
        ).pack()

        self.text = ScrolledText(
            self.root,
            bg="#12161d",
            fg="white",
            font=("Consolas", 11),
            wrap="word"
        )
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

    def set_status(self, t):
        self.status.set(t)
        self.root.update_idletasks()

    def set_progress(self, v):
        self.progress["value"] = v
        self.percent.set(f"{v}%")
        self.root.update_idletasks()

    def start(self):
        self.request_id += 1
        current_id = self.request_id

        self.btn.config(state="disabled")
        self.set_progress(0)

        threading.Thread(target=self.load, args=(current_id,), daemon=True).start()

    def load(self, rid):

        try:
            self.root.after(0, lambda: self.set_status("Descarregant..."))

            url = UPDATE_URL + f"?t={int(time.time()*1000)}"

            r = requests.get(
                url,
                timeout=20,
                headers={"Cache-Control": "no-cache"}
            )
            r.raise_for_status()

            # 🔥 si ja hi ha un altre clic després, ignora aquesta resposta
            if rid != self.request_id:
                return

            self.root.after(0, lambda: self.set_progress(100))
            self.root.after(0, lambda: self.render(r.text))
            self.root.after(0, lambda: self.set_status("Última versió carregada"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        finally:
            self.root.after(0, lambda: self.btn.config(state="normal"))

    def render(self, text):
        # 🔥 important: neteja total abans de mostrar
        self.text.delete("1.0", "end")
        self.text.insert("end", text)


root = tk.Tk()
App(root)
root.mainloop()
