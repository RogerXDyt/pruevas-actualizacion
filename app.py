import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time

VERSION_URL = "https://raw.githubusercontent.com/RogerXDyt/pruevas-actualizacion/main/version.json"


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Updater TEXT MODE")
        self.root.geometry("700x450")
        self.root.configure(bg="#111")

        self.status = tk.StringVar(value="Preparat")
        self.percent = tk.StringVar(value="0%")

        self.build_ui()

    def build_ui(self):

        title = tk.Label(
            self.root,
            text="SYSTEM UPDATE (TEXT MODE)",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#111"
        )
        title.pack(pady=10)

        self.btn = tk.Button(
            self.root,
            text="Descarregar actualització",
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

        self.log = tk.Text(
            self.root,
            height=12,
            bg="black",
            fg="lime"
        )
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def write(self, txt):
        self.log.insert("end", txt + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def set_status(self, t):
        self.status.set(t)
        self.root.update_idletasks()

    def set_percent(self, p):
        self.progress["value"] = p
        self.percent.set(f"{p}%")
        self.root.update_idletasks()

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):

        try:
            self.btn.config(state="disabled")

            self.set_status("Connectant a GitHub...")
            self.write("[INFO] Llegint version.json")

            r = requests.get(VERSION_URL)
            data = r.json()

            version = data.get("version", "desconeguda")

            self.write(f"[INFO] Versió detectada: {version}")

            self.set_status("Simulant descàrrega...")

            # SIMULACIÓ "VIDEO"
            for i in range(101):
                self.set_percent(i)

                if i == 10:
                    self.write("[OK] Inici descàrrega...")
                if i == 40:
                    self.write("[OK] Descarregant chunks...")
                if i == 70:
                    self.write("[OK] Verificant fitxer...")
                if i == 90:
                    self.write("[OK] Finalitzant instal·lació...")

                time.sleep(0.03)

            self.set_status("Actualització completada")
            self.write("[SUCCESS] Update finalitzat correctament")

            messagebox.showinfo(
                "OK",
                f"Actualitzat a versió {version}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            self.btn.config(state="normal")


root = tk.Tk()
app = App(root)
root.mainloop()
