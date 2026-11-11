"""Run once on each computer:  python check_setup.py"""
import os
import sys

print(f"Python version : {sys.version.split()[0]}")

# 1. Python packages
for name in ("flask", "pytesseract", "cv2", "PIL", "numpy"):
    try:
        __import__(name)
        print(f"[OK]   package '{name}' is installed")
    except ImportError:
        print(f"[FAIL] package '{name}' is missing -> run: pip install -r requirements.txt")

# 2. Tesseract engine
import pytesseract

default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
try:
    version = pytesseract.get_tesseract_version()
    print(f"[OK]   Tesseract found on PATH (version {version})")
except Exception:
    if os.path.exists(default_path):
        pytesseract.pytesseract.tesseract_cmd = default_path
        version = pytesseract.get_tesseract_version()
        print(f"[WARN] Tesseract works only via full path (version {version}).")
        print("       Add C:\\Program Files\\Tesseract-OCR to PATH (Step 1.4).")
    else:
        print("[FAIL] Tesseract not found. Install it (Step 1.4).")
        sys.exit(1)

# 3. Languages
try:
    langs = pytesseract.get_languages(config="")
    print(f"       Languages available: {', '.join(langs)}")
    if "eng" not in langs:
        print("[FAIL] English data missing")
    if "hin" not in langs:
        print("[WARN] Hindi data not installed (optional, re-run installer to add)")
except Exception as error:
    print(f"[WARN] Could not list languages: {error}")

print("Setup check finished.")