import uuid

def load(self, rid):
    try:
        self.root.after(0, lambda: self.status.set("Descarregant..."))

        url = UPDATE_URL + f"?id={uuid.uuid4()}"

        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()

        if rid != self.request_id:
            return

        text = r.text.strip()

        self.root.after(0, lambda: self.render(text))
        self.root.after(0, lambda: self.status.set("Última versió carregada"))

    except Exception as e:
        self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
