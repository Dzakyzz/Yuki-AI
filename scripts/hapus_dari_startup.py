import os

def hapus():
    startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")

    # Hapus shortcut .lnk (format baru)
    lnk_file = os.path.join(startup_dir, "Yuki_AI.lnk")
    # Hapus juga .vbs lama jika masih ada
    vbs_file = os.path.join(startup_dir, "YukiAI.vbs")

    removed = []

    for path, label in [(lnk_file, "Yuki_AI.lnk"), (vbs_file, "YukiAI.vbs")]:
        if os.path.exists(path):
            try:
                os.remove(path)
                removed.append(label)
            except Exception as e:
                print(f"[Error] Gagal menghapus {label}: {e}")

    print("=" * 60)
    if removed:
        print("  BERHASIL! Yuki AI telah dihapus dari Windows Startup.")
        print(f"  File dihapus: {', '.join(removed)}")
        print("=" * 60)
        print("Yuki tidak akan otomatis berjalan saat laptop dinyalakan.")
    else:
        print("  Yuki AI belum terpasang di Windows Startup.")
    print("=" * 60)

if __name__ == "__main__":
    hapus()
