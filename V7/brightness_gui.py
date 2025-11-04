#!/usr/bin/env python3
# Brightness GUI for Raspberry Pi Touch Display v2 (5")
# Author: Orion for David (WA9ONY)
# Changes: removed 0 button; shorter preset buttons

import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import subprocess

CONFIG_DIR = Path.home() / ".config" / "brightgui"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LAST_FILE = CONFIG_DIR / "last_brightness.txt"

BACKLIGHT_BASE = "/sys/class/backlight"

def detect_backlight():
    try:
        entries = [d for d in os.listdir(BACKLIGHT_BASE)
                   if os.path.isdir(os.path.join(BACKLIGHT_BASE, d))]
        if not entries:
            return None
        if "11-0045" in entries:
            return "11-0045"
        return entries[0]
    except Exception:
        return None

DEVICE = detect_backlight()
if not DEVICE:
    raise SystemExit("No /sys/class/backlight device found.")

BRIGHTNESS_PATH = f"{BACKLIGHT_BASE}/{DEVICE}/brightness"
MAX_PATH = f"{BACKLIGHT_BASE}/{DEVICE}/max_brightness"

def read_int(path, default):
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except Exception:
        return default

MAX_BRIGHT = read_int(MAX_PATH, 31)
CURR = read_int(BRIGHTNESS_PATH, MAX_BRIGHT)

def write_brightness(val: int) -> bool:
    s = str(int(val))
    try:
        with open(BRIGHTNESS_PATH, "w") as f:
            f.write(s)
        return True
    except PermissionError:
        try:
            cmd = f'echo {s} > "{BRIGHTNESS_PATH}"'
            subprocess.check_call(["pkexec", "/bin/bash", "-lc", cmd])
            return True
        except Exception:
            pass
        try:
            subprocess.run(
                ["sudo", "tee", BRIGHTNESS_PATH],
                input=(s + "\n").encode("utf-8"),
                check=True,
                stdout=subprocess.DEVNULL
            )
            return True
        except Exception:
            return False
    except Exception:
        return False

def save_last(val: int):
    try:
        LAST_FILE.write_text(str(int(val)))
    except Exception:
        pass

def load_last(default_val: int) -> int:
    try:
        v = int(LAST_FILE.read_text().strip())
        if 0 <= v <= MAX_BRIGHT:
            return v
    except Exception:
        pass
    return default_val

# GUI
root = tk.Tk()
root.title("Brightness")
root.geometry("360x210")
root.configure(bg="#111111")

title = tk.Label(root, text=f"Display Brightness ({DEVICE})",
                 fg="white", bg="#111111", font=("DejaVu Sans", 14, "bold"))
title.pack(pady=(10, 6))

percent_var = tk.StringVar()

def update_label(val: int):
    pct = int(round((val / MAX_BRIGHT) * 100))
    percent_var.set(f"{val} / {MAX_BRIGHT}  ({pct}%)")

percent = tk.Label(root, textvariable=percent_var,
                   fg="#cccccc", bg="#111111", font=("DejaVu Sans", 11))
percent.pack(pady=(0, 6))

slider = tk.Scale(root,
                  from_=0,
                  to=MAX_BRIGHT,
                  orient="horizontal",
                  length=300,
                  bg="#111111",
                  troughcolor="#333333",
                  fg="white",
                  highlightthickness=0,
                  font=("DejaVu Sans", 11))

def on_slide(_):
    val = slider.get()
    if not write_brightness(val):
        messagebox.showerror("Permission required",
                             "Couldn't write brightness.\n\nRun with sudo or install the udev rule.")
        slider.set(read_int(BRIGHTNESS_PATH, val))
        return
    update_label(val)
    save_last(val)

slider.pack(pady=4)
slider.configure(command=on_slide)

# Preset buttons (0 removed; shorter width)
btn_frame = tk.Frame(root, bg="#111111")
btn_frame.pack(pady=8)

PRESETS = [5, 8, 10, 15, 20, 25, MAX_BRIGHT]  # 0 removed

def make_btn(v):
    def _set():
        slider.set(v)
        on_slide(None)
    b = tk.Button(btn_frame, text=str(v), width=2, command=_set)  # width shortened
    b.pack(side="left", padx=2)
for v in PRESETS:
    make_btn(v)

start_val = load_last(min(CURR, MAX_BRIGHT))
slider.set(start_val)
update_label(start_val)

root.mainloop()
