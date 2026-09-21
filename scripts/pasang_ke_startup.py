import os
import sys

def pasang():
    # Folder Startup Windows
    startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
    lnk_file = os.path.join(startup_dir, "Yuki_AI.lnk")

    # Menggunakan pythonw.exe agar TIDAK muncul jendela hitam CMD saat laptop dinyalakan
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    # Lokasi file target (main.py di folder root project)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # naik satu level dari scripts/
    target_script = os.path.join(base_dir, "main.py")

    try:
        import winreg  # noqa - just to confirm Windows
        import subprocess

        # Buat shortcut (.lnk) menggunakan PowerShell
        ps_cmd = (
            f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{lnk_file}");'
            f'$s.TargetPath="{pythonw}";'
            f'$s.Arguments=\'"{target_script}"\';'
            f'$s.WorkingDirectory="{base_dir}";'
            f'$s.WindowStyle=7;'  # 7 = minimized (tidak muncul jendela)
            f'$s.Description="Yuki AI Virtual Girlfriend";'
            f'$s.Save()'
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"[Error] PowerShell: {result.stderr.strip()}")
            return

        print("=" * 65)
        print("  BERHASIL! Yuki AI sudah dipasang ke Windows Startup.")
        print(f"  Target File  : {target_script}")
        print(f"  Startup File : {lnk_file}")
        print("=" * 65)
        print("Mulai sekarang, saat Anda menyalakan laptop:")
        print("-> Yuki akan otomatis muncul di pojok kanan bawah desktop")
        print("-> Tanpa jendela hitam CMD sama sekali (bersih & mulus)!")
        print("=" * 65)

    except Exception as e:
        print(f"[Error] Gagal memasang ke startup: {e}")

if __name__ == "__main__":
    pasang()
