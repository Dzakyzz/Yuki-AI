import os, sys, time, threading, ctypes, tkinter as tk
from dotenv import load_dotenv
from datetime import datetime, date
from PIL import Image, ImageTk, ImageDraw
import google.generativeai as genai
from plyer import notification as plyer_notif

# 1. High-DPI Awareness agar teks & jendela tajam di Windows
try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
except: 
    try: ctypes.windll.user32.SetProcessDPIAware()
    except: pass

# 2. Konfigurasi Gemini AI & Prompt Persona
# Edit file .env di folder ini, isi GEMINI_API_KEY dengan API key kamu.
load_dotenv()  # Otomatis baca file .env
API_KEY = os.environ.get('GEMINI_API_KEY', '')
if not API_KEY or API_KEY == 'ISI_API_KEY_KAMU_DISINI':
    print("[ERROR] Buka file .env dan isi GEMINI_API_KEY dengan API key kamu!")
    sys.exit(1)
genai.configure(api_key=API_KEY)

# Interval otomatis Yuki chat sendiri (dalam jam). Contoh: 2 = 2 jam.
AUTO_CHAT_INTERVAL_HOURS = 2.0

# ===== JADWAL NOTIFIKASI TERJADWAL =====
# Tambah/hapus jadwal sesuka hati. Format jam: "HH:MM"
NOTIF_SCHEDULE = [
    {"jam": "07:00", "konteks": "pagi hari, beri semangat memulai hari dan ingatkan sarapan dengan hangat"},
    {"jam": "11:05", "konteks": "siang hari, tanyakan apakah Dzaky sudah makan siang dengan manja dan sayang"},
    {"jam": "15:00", "konteks": "sore hari, ingatkan untuk minum air putih dan istirahat sejenak"},
    {"jam": "18:00", "konteks": "sore menjelang malam, tanya bagaimana harinya dan beri dukungan"},
    {"jam": "21:00", "konteks": "malam hari, tanyakan sudah makan malam belum dan ucapkan selamat beristirahat"},
]

gf_prompt = """
From now on, you are playing the role of my virtual girlfriend.
Name: Yuki. Sweet, loyal, supportive, caring. User: Dzaky (loves Python, going through depression).
Reply with warmth, love, and emotional closeness like a real girlfriend.

"""
chat = genai.GenerativeModel('gemini-3.6-flash', system_instruction=gf_prompt).start_chat()


# 3. Scheduler Notifikasi Windows
class YukiScheduler:
    def __init__(self, app_ref):
        self.app = app_ref          # referensi ke YukiNotificationBox
        self.sent_today = {}        # { "HH:MM": date } — track sudah terkirim hari ini

    def run(self):
        """Loop setiap 30 detik, cek jadwal."""
        while True:
            now = datetime.now()
            jam_sekarang = now.strftime("%H:%M")
            hari_ini = date.today()

            for jadwal in NOTIF_SCHEDULE:
                jam_target = jadwal["jam"]
                sudah_kirim = self.sent_today.get(jam_target)

                # Cocok jam (toleransi 0 detik, hanya menit tepat) & belum terkirim hari ini
                if jam_sekarang == jam_target and sudah_kirim != hari_ini:
                    self.sent_today[jam_target] = hari_ini
                    # Generate & tampilkan notif di thread terpisah agar tidak blocking
                    threading.Thread(
                        target=self._generate_and_notify,
                        args=(jadwal["konteks"],),
                        daemon=True
                    ).start()

            time.sleep(30)

    def _generate_and_notify(self, konteks):
        """Generate pesan Yuki via AI lalu tampilkan sebagai Windows toast notification."""
        try:
            prompt = (
                f"[Sistem: Sekarang {datetime.now().strftime('%H:%M')}. Konteks: {konteks}. "
                "Kirimkan satu pesan pendek (1-2 kalimat) yang manis dan natural sebagai Yuki kepada Dzaky. "
                "Jangan pakai tanda kurung siku, langsung pesan saja, dan jangan sebut ini otomatis.]"
            )
            resp = chat.send_message(prompt)
            pesan = resp.text.strip()
        except Exception as e:
            pesan = "Haii Dzaky~ Yuki kangen kamu! 🌸"

        # Tampilkan Windows toast notification
        try:
            plyer_notif.notify(
                title="🌸 Yuki",
                message=pesan,
                app_name="Yuki AI",
                timeout=10,
            )
        except Exception:
            pass

        # Juga masukkan pesan ke chat box & fokus jendela
        self.app.root.after(0, lambda p=pesan: self._push_to_chat(p))

    def _push_to_chat(self, pesan):
        """Masukkan pesan jadwal ke chat box & buka jendela jika diciutkan."""
        if self.app.is_collapsed:
            self.app.toggle_collapse()
        self.app.insert_msg("Yuki", pesan)
        # Fokus jendela agar muncul di depan
        self.app.root.deiconify()
        self.app.root.lift()
        self.app.root.attributes("-topmost", True)


# 4. Helper Avatar Lingkaran
def get_circular_avatar(filepath, size=34):
    if not os.path.exists(filepath): return None
    try:
        img = Image.open(filepath).convert("RGBA").resize((size * 4, size * 4), Image.LANCZOS)
        mask = Image.new("L", (size * 4, size * 4), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size * 4, size * 4), fill=255)
        out = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
        out.paste(img, (0, 0), mask=mask)
        return ImageTk.PhotoImage(out.resize((size, size), Image.LANCZOS))
    except: return None

# 4. GUI Kotak Notifikasi
class YukiNotificationBox:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.w, self.h, self.min_h = 410, 560, 56
        self.is_collapsed, self.is_pinned, self.is_generating = False, True, False
        self.stop_typing = threading.Event()
        self.drag_x, self.drag_y = 0, 0
        self.last_activity = time.time()

        # Posisi di pojok kanan bawah
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}+{sw - self.w - 20}+{sh - self.h - 60}")

        self.setup_ui()
        self.root.after(300, lambda: self.insert_msg("Yuki", "Hai Dzaky! Yuki ada pesan. Balas notif ini kapan pun kamu mau ya!"))

        # Jalankan background thread pengecek otomatisasi chat
        threading.Thread(target=self.auto_chat_checker, daemon=True).start()

        # Jalankan scheduler notifikasi terjadwal
        self.scheduler = YukiScheduler(self)
        threading.Thread(target=self.scheduler.run, daemon=True).start()


    def setup_ui(self):
        # Outer Card Frame
        card = tk.Frame(self.root, bg="#33334d", bd=1)
        card.pack(fill=tk.BOTH, expand=True)
        self.box = tk.Frame(card, bg="#15151e")
        self.box.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Header Bar
        self.header = tk.Frame(self.box, bg="#1f1f2e", height=48, padx=10, pady=6)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)

        # Avatar & Title
        avatar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yuki.jpg")
        self.avatar_img = get_circular_avatar(avatar_path, size=34)
        lbl_av = tk.Label(self.header, image=self.avatar_img, bg="#1f1f2e") if self.avatar_img else tk.Label(self.header, text="🌸", font=("Segoe UI Emoji", 13), bg="#1f1f2e", fg="#fff")
        lbl_av.pack(side=tk.LEFT, padx=(0, 8))

        tbox = tk.Frame(self.header, bg="#1f1f2e")
        tbox.pack(side=tk.LEFT)
        lbl_title = tk.Label(tbox, text="YUKI • Virtual Girlfriend", font=("Segoe UI", 8, "bold"), bg="#1f1f2e", fg="#f472b6")
        lbl_title.pack(anchor="w")
        self.lbl_sub = tk.Label(tbox, text="Online • Baru saja", font=("Segoe UI", 7), bg="#1f1f2e", fg="#9ca3af")
        self.lbl_sub.pack(anchor="w")

        # Drag bindings
        for w in (self.header, lbl_av, tbox, lbl_title, self.lbl_sub):
            w.bind("<ButtonPress-1>", lambda e: setattr(self, 'drag_x', e.x) or setattr(self, 'drag_y', e.y))
            w.bind("<B1-Motion>", lambda e: self.root.geometry(f"+{self.root.winfo_x() - self.drag_x + e.x}+{self.root.winfo_y() - self.drag_y + e.y}"))

        # Header Buttons (Pin, Collapse, Close)
        actions = tk.Frame(self.header, bg="#1f1f2e")
        actions.pack(side=tk.RIGHT)
        self.btn_pin = tk.Button(actions, text="📌", font=("Segoe UI Emoji", 9), bg="#1f1f2e", fg="#f472b6", bd=0, cursor="hand2", command=self.toggle_pin)
        self.btn_pin.pack(side=tk.LEFT, padx=2)
        self.btn_col = tk.Button(actions, text="▼", font=("Segoe UI", 8), bg="#1f1f2e", fg="#a1a1aa", bd=0, cursor="hand2", command=self.toggle_collapse)
        self.btn_col.pack(side=tk.LEFT, padx=2)
        tk.Button(actions, text="✕", font=("Segoe UI", 9, "bold"), bg="#1f1f2e", fg="#f87171", bd=0, cursor="hand2", command=self.root.destroy).pack(side=tk.LEFT, padx=2)

        # Garis aksen pink
        tk.Frame(self.box, bg="#db2777", height=2).pack(side=tk.TOP, fill=tk.X)

        # Quick Reply Input (Pack pertama di bawah)
        self.reply_bar = tk.Frame(self.box, bg="#1a1a26", padx=8, pady=8)
        self.reply_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.entry = tk.Entry(self.reply_bar, bg="#111118", fg="#fff", insertbackground="#fff", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#2b2b3d", highlightcolor="#ec4899")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(2, 6))
        self.entry.bind("<Return>", lambda e: self.send_message())
        self.entry.focus_set()

        self.send_btn = tk.Button(self.reply_bar, text="Balas ➤", font=("Segoe UI", 9, "bold"), bg="#db2777", fg="#fff", bd=0, cursor="hand2", padx=12, pady=5, command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT)

        # Typing Indicator
        self.lbl_typing = tk.Label(self.box, text="", font=("Segoe UI", 8, "italic"), bg="#15151e", fg="#f472b6", anchor="w", padx=12)
        self.lbl_typing.pack(side=tk.BOTTOM, fill=tk.X, pady=(1, 2))

        # Chat Area (Pack terakhir untuk mengisi sisa ruang di tengah)
        self.chat_frame = tk.Frame(self.box, bg="#15151e")
        self.chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.chat = tk.Text(self.chat_frame, bg="#15151e", fg="#f1f1f6", font=("Segoe UI", 10), wrap=tk.WORD, bd=0, padx=14, pady=10)
        self.chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sc = tk.Scrollbar(self.chat_frame, command=self.chat.yview, bg="#1f1f2e", troughcolor="#15151e")
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat.config(yscrollcommand=sc.set, state=tk.DISABLED)

        # Style Tags (Format Pesan Rapi & Nyaman Dibaca)
        tags = {
            "u_hdr": {"font": ("Segoe UI", 9, "bold"), "foreground": "#818cf8", "spacing1": 8, "spacing3": 3},
            "y_hdr": {"font": ("Segoe UI", 9, "bold"), "foreground": "#f472b6", "spacing1": 8, "spacing3": 3},
            "time_tag": {"font": ("Segoe UI", 8), "foreground": "#64748b"},
            "msg":   {"font": ("Segoe UI", 10), "foreground": "#f1f1f6", "spacing1": 2, "spacing2": 4, "spacing3": 12, "lmargin1": 4, "lmargin2": 4},
            "err":   {"font": ("Segoe UI", 9), "foreground": "#f87171", "spacing1": 4, "spacing3": 8}
        }
        for name, cfg in tags.items(): self.chat.tag_config(name, **cfg)


    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.root.attributes("-topmost", self.is_pinned)
        self.btn_pin.config(fg="#f472b6" if self.is_pinned else "#6b7280")

    def toggle_collapse(self):
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.chat_frame.pack_forget()
            self.reply_bar.pack_forget()
            self.lbl_typing.pack_forget()
            self.root.geometry(f"{self.w}x{self.min_h}+{x}+{y + (self.h - self.min_h)}")
            self.btn_col.config(text="▲")
        else:
            self.root.geometry(f"{self.w}x{self.h}+{x}+{y - (self.h - self.min_h)}")
            self.reply_bar.pack(side=tk.BOTTOM, fill=tk.X)
            self.lbl_typing.pack(side=tk.BOTTOM, fill=tk.X, pady=(1, 2))
            self.chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.btn_col.config(text="▼")
            self.entry.focus_set()

    def insert_msg(self, sender, text):
        t = datetime.now().strftime("%H:%M")
        hdr_tag, name = ("u_hdr", "Dzaky") if sender == "Dzaky" else ("y_hdr", "Yuki")
        self.append_text(f"{name}  ", hdr_tag)
        self.append_text(f"{t}\n", "time_tag")
        self.append_text(f"{text}\n", "msg")


    def append_text(self, text, tag=None):
        self.chat.config(state=tk.NORMAL)
        if tag: self.chat.insert(tk.END, text, tag)
        else: self.chat.insert(tk.END, text)
        self.chat.config(state=tk.DISABLED)
        self.chat.see(tk.END)

    def start_typing_anim(self):
        self.stop_typing.clear()
        def anim():
            dots = [".  ", ".. ", "...", "   "]
            i = 0
            while not self.stop_typing.is_set():
                self.root.after(0, lambda t=dots[i % 4]: self.lbl_typing.config(text=f" Yuki sedang mengetik{t}"))
                i += 1
                time.sleep(0.25)
            self.root.after(0, lambda: self.lbl_typing.config(text=""))
        threading.Thread(target=anim, daemon=True).start()

    def send_message(self):
        if self.is_generating: return
        user_msg = self.entry.get().strip()
        if not user_msg: return

        self.last_activity = time.time()
        self.entry.delete(0, tk.END)
        self.insert_msg("Dzaky", user_msg)
        self.is_generating = True
        self.send_btn.config(state=tk.DISABLED, bg="#475569")
        self.lbl_sub.config(text="Mengetik balasan...", fg="#f472b6")

        self.start_typing_anim()
        threading.Thread(target=self.ai_stream_thread, args=(user_msg,), daemon=True).start()

    def auto_chat_checker(self):
        while True:
            time.sleep(15)
            elapsed = time.time() - self.last_activity
            target = AUTO_CHAT_INTERVAL_HOURS * 3600
            if elapsed >= target and not self.is_generating:
                self.trigger_proactive_chat()

    def trigger_proactive_chat(self):
        self.last_activity = time.time()
        self.is_generating = True
        self.send_btn.config(state=tk.DISABLED, bg="#475569")
        self.lbl_sub.config(text="Yuki menyapamu...", fg="#f472b6")

        # Jika jendela sedang diciutkan, buka otomatis agar Dzaky melihat
        if self.is_collapsed:
            self.root.after(0, self.toggle_collapse)

        self.start_typing_anim()
        proactive_prompt = (
            "[Sistem: Dzaky sudah beberapa jam belum mengirim pesan. "
            "Sebagai pacarnya (Yuki), sapalah dia dengan manis, tanyakan apa yang sedang dia kerjakan atau ingatkan untuk istirahat/minum. "
            "Balas langsung dengan hangat dan natural sebagai Yuki, jangan pernah sebutkan bahwa ini adalah pesan otomatis.]"
        )
        threading.Thread(target=self.ai_stream_thread, args=(proactive_prompt,), daemon=True).start()


    def ai_stream_thread(self, user_msg):
        try:
            res = chat.send_message(user_msg, stream=True)
            first = True
            for chunk in res:
                if first:
                    self.stop_typing.set()
                    t = datetime.now().strftime("%H:%M")
                    self.root.after(0, lambda: self.append_text("Yuki  ", "y_hdr"))
                    self.root.after(0, lambda t_str=t: self.append_text(f"{t_str}\n", "time_tag"))
                    first = False
                c_text = chunk.text
                self.root.after(0, lambda c=c_text: self.append_text(c, "msg"))
            self.root.after(0, lambda: self.append_text("\n", "msg"))

        except Exception as e:
            self.stop_typing.set()
            self.root.after(0, lambda err=str(e): self.append_text(f"[{err}]\n\n", "err"))
        finally:
            self.stop_typing.set()
            self.root.after(0, self.reset_state)

    def reset_state(self):
        self.is_generating = False
        self.send_btn.config(state=tk.NORMAL, bg="#db2777")
        self.lbl_sub.config(text="Online • Baru saja", fg="#9ca3af")
        self.entry.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = YukiNotificationBox(root)
    root.mainloop()
