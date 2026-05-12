import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

UPDATE_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/update.txt"


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Updater TEXT")
        self.root.geometry("800x500")
        self.root.configure(bg="#111")

        self.status = tk.StringVar(value="Preparat")
        self.percent = tk.StringVar(value="0%")

        self.build_ui()

    def build_ui(self):

        title = tk.Label(
            self.root,
            text="SYSTEM UPDATE",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#111"
        )
        title.pack(pady=10)

        self.btn = tk.Button(
            self.root,
            text="Carregar actualització",
            command=self.start,
            bg="#00aa44",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            width=25
        )
        self.btn.pack(pady=10)

        self.progress = ttk.Progressbar(
            self.root,
            length=500,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(pady=10)

        tk.Label(
            self.root,
            textvariable=self.percent,
            fg="white",
            bg="#111"
        ).pack()

        tk.Label(
            self.root,
            textvariable=self.status,
            fg="#ccc",
            bg="#111"
        ).pack(pady=5)

        self.text = tk.Text(
            self.root,
            bg="black",
            fg="lime",
            font=("Consolas", 11)
        )
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

    def set_status(self, t):
        self.status.set(t)
        self.root.update_idletasks()

    def set_percent(self, p):
        self.progress["value"] = p
        self.percent.set(f"{p}%")
        self.root.update_idletasks()

    def start(self):
        threading.Thread(target=self.load_update, daemon=True).start()

    def load_update(self):

        try:
            self.btn.config(state="disabled")

            self.set_status("Connectant a GitHub...")
            self.set_percent(20)

            r = requests.get(UPDATE_URL)
            r.raise_for_status()

            self.set_percent(60)

            text = r.text

            self.set_status("Mostrant actualització...")
            self.set_percent(100)

            self.text.delete("1.0", "end")
            self.text.insert("end", text)

            messagebox.showinfo("OK", "Actualització carregada")

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            self.btn.config(state="normal")


root = tk.Tk()
app = App(root)
root.mainloop()
