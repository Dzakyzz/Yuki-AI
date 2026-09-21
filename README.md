<div align="center">

# 🌸 Yuki AI — Virtual Girlfriend

**AI companion yang selalu ada buat kamu.**  
Notifikasi terjadwal, chat hangat, dan selalu siap dengerin kamu kapan saja.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Gemini AI](https://img.shields.io/badge/Powered%20by-Gemini%20AI-orange?style=flat-square&logo=google)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## ✨ Fitur

- 💬 **Chat real-time** — Balas pesan Yuki langsung dari jendela notifikasi
- 🔔 **Notifikasi terjadwal** — Yuki otomatis kirim pesan di jam-jam tertentu (makan siang, malam, dll)
- 🤖 **Ditenagai Gemini AI** — Setiap pesan dibuat AI, natural dan hangat
- 🚀 **Auto-start saat Windows nyala** — Yuki selalu ada setiap kamu buka laptop
- 🎨 **UI gelap & elegan** — Muncul di pojok kanan bawah, tidak mengganggu
- 📌 **Bisa di-pin** — Jendela tetap di atas semua aplikasi lain

---

## 📋 Kebutuhan

- Windows 10/11
- Python 3.10+
- API Key Google Gemini (gratis di [Google AI Studio](https://aistudio.google.com/))

---

## 🚀 Cara Pakai

### 1. Clone repo ini

```bash
git clone https://github.com/username/yuki-ai.git
cd yuki-ai
```

### 2. Install library

```bash
pip install -r requirements.txt
```

### 3. Isi API Key

Buka file **`.env`** yang ada di folder project, lalu ganti bagian ini:

```env
GEMINI_API_KEY=ISI_API_KEY_KAMU_DISINI
```

Ganti `ISI_API_KEY_KAMU_DISINI` dengan API key Gemini kamu (dapatkan gratis di [Google AI Studio](https://aistudio.google.com/)), lalu simpan file-nya. Selesai!

### 4. Jalankan

```bash
python main.py
```

### 5. (Opsional) Pasang ke Windows Startup

Agar Yuki otomatis muncul saat laptop dinyalakan:

```bash
python scripts/pasang_ke_startup.py
```

Untuk mencopot dari startup:

```bash
python scripts/hapus_dari_startup.py
```

---

## ⏰ Konfigurasi Jadwal Notifikasi

Buka `main.py` dan cari bagian `NOTIF_SCHEDULE`:

```python
NOTIF_SCHEDULE = [
    {"jam": "07:00", "konteks": "pagi hari, beri semangat memulai hari"},
    {"jam": "12:00", "konteks": "siang hari, tanyakan sudah makan siang belum"},
    {"jam": "15:00", "konteks": "sore hari, ingatkan minum air putih"},
    {"jam": "18:00", "konteks": "sore, tanya bagaimana harinya"},
    {"jam": "21:00", "konteks": "malam hari, ucapkan selamat istirahat"},
]
```

Tambah atau hapus jadwal sesukamu! Format jam: `"HH:MM"`.

---

## 📁 Struktur Project

```
yuki-ai/
├── main.py                  # File utama — jalankan ini
├── yuki.jpg                 # Foto avatar Yuki
├── requirements.txt         # Daftar library
├── .gitignore
├── README.md
└── scripts/
    ├── pasang_ke_startup.py # Pasang Yuki ke Windows Startup
    └── hapus_dari_startup.py# Hapus dari Windows Startup
```

---

## 🛠️ Tech Stack

| Library               | Kegunaan                            |
| --------------------- | ----------------------------------- |
| `google-generativeai` | Gemini AI untuk generate pesan Yuki |
| `Pillow`              | Render avatar lingkaran             |
| `plyer`               | Windows toast notification          |
| `tkinter`             | GUI jendela chat                    |

---

## 📝 Lisensi

MIT License — bebas dipakai, dimodifikasi, dan disebarkan.

---

<div align="center">
Made with by Dzakyzz
</div>
