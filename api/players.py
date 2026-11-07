import re
import threading
import tkinter as tk
from datetime import datetime

import requests

URL = "http://kota2.indopride.id:30120"
TIMEOUT = 1
INTERVAL = 1  # detik

BG = "#0f1220"
CARD = "#181c30"
TEXT = "#f2f4f8"
MUTED = "#8b93a7"
ACCENT = "#f97316"
OK = "#22c55e"
BAD = "#ef4444"

root = tk.Tk()
root.title("Status Server FiveM")
root.configure(bg=BG)
root.geometry("380x500")
root.resizable(False, False)

card = tk.Frame(root, bg=CARD, padx=30, pady=30)
card.pack(expand=True, fill="both", padx=18, pady=18)

logo = tk.Label(card, text="🎮", font=("Segoe UI Emoji", 44), bg=CARD, fg=TEXT)
logo.pack(pady=(0, 10))

nama = tk.Label(card, text="Memuat...", font=("Segoe UI", 14, "bold"),
                bg=CARD, fg=TEXT, wraplength=300)
nama.pack()

status = tk.Label(card, text="● Menghubungkan", font=("Segoe UI", 10, "bold"),
                  bg=CARD, fg=MUTED)
status.pack(pady=(6, 14))

jumlah = tk.Label(card, text="0", font=("Segoe UI", 54, "bold"), bg=CARD, fg=ACCENT)
jumlah.pack()

maks = tk.Label(card, text="dari 0 slot", font=("Segoe UI", 11), bg=CARD, fg=MUTED)
maks.pack()

tk.Label(card, text="PLAYER ONLINE", font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(pady=(10, 14))

BAR_W, BAR_H = 300, 10
bar = tk.Canvas(card, width=BAR_W, height=BAR_H, bg="#2a2f4a", highlightthickness=0)
bar.pack()
isi = bar.create_rectangle(0, 0, 0, BAR_H, fill=ACCENT, width=0)

persen = tk.Label(card, text="0%", font=("Segoe UI", 9), bg=CARD, fg=MUTED)
persen.pack(pady=(6, 0))

update = tk.Label(card, text="-", font=("Segoe UI", 9), bg=CARD, fg=MUTED)
update.pack(side="bottom")

logo_img = None
logo_sudah = False


def bersihkan(s):
    return re.sub(r"\^\d", "", str(s)).strip()


def ambil():
    p = requests.get(f"{URL}/players.json", timeout=TIMEOUT).json()
    info = requests.get(f"{URL}/info.json", timeout=TIMEOUT).json()
    v = info.get("vars", {})
    return {
        "online": len(p),
        "max": int(v.get("sv_maxClients", 0) or 0),
        "nama": v.get("sv_projectName") or v.get("sv_hostname") or "FiveM Server",
        "icon": info.get("icon"),
    }


def set_logo(icon):
    global logo_img, logo_sudah
    logo_sudah = True
    if not icon:
        return
    try:
        img = tk.PhotoImage(data=icon)
        if img.width() > 128:
            img = img.subsample(max(1, img.width() // 96))
        logo_img = img  # simpan referensi supaya tidak dihapus Python
        logo.config(image=logo_img, text="")
    except tk.TclError:
        pass  # tetap pakai ikon 🎮


def tampil(d):
    if not logo_sudah:
        set_logo(d["icon"])
    nama.config(text=bersihkan(d["nama"]))
    jumlah.config(text=f"{d['online']:,}".replace(",", "."))
    maks.config(text=f"dari {d['max']:,} slot".replace(",", "."))
    p = (d["online"] / d["max"] * 100) if d["max"] else 0
    bar.coords(isi, 0, 0, BAR_W * min(p, 100) / 100, BAR_H)
    persen.config(text=f"{p:.1f}% slot terisi")
    status.config(text="● Online", fg=OK)
    update.config(text=f"Diperbarui {datetime.now():%H:%M:%S}")
    root.title(f"{d['online']} online - {bersihkan(d['nama'])}")


def gagal(pesan):
    status.config(text="● Tidak terhubung", fg=BAD)
    update.config(text=f"Error: {pesan[:45]}")


def worker():
    try:
        d = ambil()
        root.after(0, tampil, d)
    except Exception as e:
        root.after(0, gagal, str(e))


def refresh():
    threading.Thread(target=worker, daemon=True).start()
    root.after(INTERVAL * 1000, refresh)


refresh()
root.mainloop()
