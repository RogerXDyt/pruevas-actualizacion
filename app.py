import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import requests

UPDATE_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/update.txt"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Update Viewer")
        self.root.geometry("860x560")
        self.root.configure(bg="#0f1115")

        self.status = tk.StringVar(value="Preparat")
        self.percent = tk.StringVar(value="0%")

        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.root, bg="#0f1115")
        top.pack(fill="x", pady=(14, 8))

        tk.Label(
            top,
            text="SYSTEM UPDATE",
            font=("Segoe UI", 22, "bold"),
            fg="#ffffff",
            bg="#0f1115"
        ).pack()

        tk.Label(
            top,
            text="Carrega el text real des de GitHub",
            font=("Segoe UI", 10),
            fg="#aab2c0",
            bg="#0f1115"
        ).pack(pady=(2, 0))

        buttons = tk.Frame(self.root, bg="#0f1115")
        buttons.pack(pady=10)

        self.btn = tk.Button(
            buttons,
            text="Carregar update.txt",
            command=self.start,
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#1f8fff",
            activebackground="#1673cc",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=10
        )
        self.btn.grid(row=0, column=0, padx=8)

        self.progress = ttk.Progressbar(
            buttons,
            orient="horizontal",
            length=320,
            mode="determinate",
            maximum=100
        )
        self.progress.grid(row=0, column=1, padx=8)

        tk.Label(
            buttons,
            textvariable=self.percent,
            font=("Segoe UI", 11, "bold"),
            fg="#ffffff",
            bg="#0f1115"
        ).grid(row=0, column=2, padx=8)

        tk.Label(
            self.root,
            textvariable=self.status,
            font=("Segoe UI", 10),
            fg="#c8d0dc",
            bg="#0f1115"
        ).pack(pady=(0, 10))

        self.text = ScrolledText(
            self.root,
            bg="#12161d",
            fg="#e8eef7",
            insertbackground="white",
            font=("Consolas", 11),
            relief="flat",
            padx=14,
            pady=14,
            wrap="word"
        )
        self.text.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.text.tag_configure("title", foreground="#7dd3fc", font=("Consolas", 18, "bold"))
        self.text.tag_configure("section", foreground="#fbbf24", font=("Consolas", 14, "bold"))
        self.text.tag_configure("bullet", foreground="#86efac", font=("Consolas", 11))
        self.text.tag_configure("normal", foreground="#e8eef7", font=("Consolas", 11))
        self.text.tag_configure("muted", foreground="#9aa4b2", font=("Consolas", 10, "italic"))
        self.text.tag_configure("line", foreground="#334155", font=("Consolas", 11))

        self.render_placeholder()

    def render_placeholder(self):
        self.text.delete("1.0", "end")
        self.text.insert("end", "Aquí es mostrarà l'update.txt real.\n\n", "title")
        self.text.insert("end", "Prem el botó per descarregar-lo des de GitHub Raw.\n", "normal")
        self.text.insert("end", "El text pot portar #, ## i llistes amb - per decorar-se automàticament.\n", "muted")

    def set_status(self, value):
        self.status.set(value)
        self.root.update_idletasks()

    def set_percent(self, value):
        self.progress["value"] = value
        self.percent.set(f"{value}%")
        self.root.update_idletasks()

    def start(self):
        self.btn.config(state="disabled")
        threading.Thread(target=self.load_update, daemon=True).start()

    def load_update(self):
        try:
            self.root.after(0, lambda: self.set_status("Descarregant update.txt..."))
            self.root.after(0, lambda: self.set_percent(10))

            r = requests.get(UPDATE_URL, timeout=20)
            r.raise_for_status()

            self.root.after(0, lambda: self.set_percent(100))
            self.root.after(0, lambda: self.set_status("Text descarregat"))
            self.root.after(0, lambda: self.render_text(r.text))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.set_status("Error en la descàrrega"))
        finally:
            self.root.after(0, lambda: self.btn.config(state="normal"))

    def render_text(self, raw_text):
        self.text.delete("1.0", "end")

        lines = raw_text.splitlines()
        first_title_done = False

        for line in lines:
            stripped = line.strip()

            if not stripped:
                self.text.insert("end", "\n")
                continue

            if stripped.startswith("# "):
                title = stripped[2:].strip()
                if not first_title_done:
                    self.text.insert("end", title + "\n", "title")
                    self.text.insert("end", "=" * max(18, len(title)) + "\n\n", "line")
                    first_title_done = True
                else:
                    self.text.insert("end", title + "\n", "section")
                    self.text.insert("end", "-" * max(12, len(title)) + "\n", "line")

            elif stripped.startswith("## "):
                section = stripped[3:].strip()
                self.text.insert("end", section + "\n", "section")
                self.text.insert("end", "-" * max(12, len(section)) + "\n", "line")

            elif stripped.startswith("- "):
                self.text.insert("end", "• " + stripped[2:].strip() + "\n", "bullet")

            else:
                self.text.insert("end", stripped + "\n", "normal")


root = tk.Tk()
app = App(root)
root.mainloop()
