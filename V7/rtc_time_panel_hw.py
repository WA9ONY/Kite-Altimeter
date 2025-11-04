#!/usr/bin/env python3
"""
rtc_time_panel_hw.py (robust)
Show System Clock and RTC clock without touching the I2C bus.
Strategy:
1) Try hwclock --show from common locations; capture stderr if it fails.
2) If hwclock fails/unavailable, fall back to /proc/driver/rtc (read-only).
"""

import os
import subprocess
import tkinter as tk
from datetime import datetime

REFRESH_MS = 1000

def _try_hwclock():
    candidates = ["/usr/sbin/hwclock", "/sbin/hwclock", "hwclock"]
    for exe in candidates:
        try:
            r = subprocess.run([exe, "--show"], capture_output=True, text=True, check=False)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
            else:
                # keep last error to report if all candidates fail
                last_err = (r.stderr or f"{exe} exit {r.returncode}").strip()
        except FileNotFoundError:
            last_err = f"{exe} not found"
        except Exception as e:
            last_err = f"{exe} error: {e}"
    return f"(hwclock error: {last_err})"

def _try_proc_driver_rtc():
    # Many systems expose a human-readable RTC snapshot here.
    p = "/proc/driver/rtc"
    try:
        if os.path.exists(p):
            with open(p, "r") as f:
                lines = f.read().splitlines()
            # Find the 'rtc_time' and 'rtc_date' fields
            tline = next((ln for ln in lines if ln.lower().startswith("rtc_time")), None)
            dline = next((ln for ln in lines if ln.lower().startswith("rtc_date")), None)
            if tline and dline:
                t = tline.split(":", 1)[1].strip()
                d = dline.split(":", 1)[1].strip()
                # rtc_time is usually HH:MM:SS and rtc_date is YYYY-MM-DD
                return f"{d} {t} (from /proc/driver/rtc)"
    except Exception as e:
        return f"(/proc/driver/rtc error: {e})"
    return None

def read_rtc_string():
    s = _try_hwclock()
    if s.startswith("(hwclock error:"):
        # try fallback
        alt = _try_proc_driver_rtc()
        if alt:
            return alt
    return s

def read_sysclock():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

root = tk.Tk()
root.title("System & RTC Clocks")
root.geometry("460x170+60+60")

f = tk.Frame(root, padx=14, pady=14)
f.pack(fill="both", expand=True)

lbl1h = tk.Label(f, text="System Clock:", font=("Arial", 14, "bold"), anchor="w")
lbl1h.grid(row=0, column=0, sticky="w")
lbl1  = tk.Label(f, text="--", font=("Arial", 14), anchor="w")
lbl1.grid(row=0, column=1, sticky="w", padx=(8,0))

lbl2h = tk.Label(f, text="RTC (kernel):", font=("Arial", 14, "bold"), anchor="w")
lbl2h.grid(row=1, column=0, sticky="w", pady=(8,0))
lbl2  = tk.Label(f, text="--", font=("Arial", 14), anchor="w", justify="left")
lbl2.grid(row=1, column=1, sticky="w", padx=(8,0), pady=(8,0))

def tick():
    lbl1.config(text=read_sysclock())
    lbl2.config(text=read_rtc_string())
    root.after(REFRESH_MS, tick)

root.after(10, tick)
root.mainloop()
