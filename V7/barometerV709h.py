#!/usr/bin/env python3
# barometerV709h.py — V7.09h
# Single bottom strip-chart (1 px = 1 sample), DSP smoothing control,
# NOAA 60-sample mean (green) + text, DPS310 real sensor in high-precision mode.
import os, sys, csv, time, shutil, subprocess, tkinter as tk
from tkinter import messagebox
from collections import deque
from datetime import datetime, timezone

# ───── Hardware libs (required) ─────
import board, busio
import adafruit_dps310
try:
    import adafruit_ds3231  # optional; used only if present
except Exception:
    adafruit_ds3231 = None

PROGRAM_ID = "V709h"
VERSION_STRING = "Atmospheric Pressure Logger V7.09h / HW7 SW09h"

SAMPLE_INTERVAL = 1.0           # seconds
STRIP_HISTORY = []              # persistent for the strip chart
SMOOTH_WINDOW = 10              # user-adjustable smoothing window (samples)
NOAA_SMOOTH_N = 60              # fixed 60-sample mean for NOAA line/label

# Buffers
WIN_1MIN = 60
buf_1min = deque(maxlen=WIN_1MIN)

# UI theme
ROOT_BG = "#add8e6"
HEADER = ("Arial", 16, "bold")
DATA   = ("Arial", 14)
LABELF = ("Arial", 12, "bold")

# ───── Utility functions ─────
def hpa_to_inhg(h): return h / 33.8638866667
def c_to_f(c): return c * 9 / 5 + 32
def sea_level_pressure_hpa(p, h_m): return p / pow((1.0 - h_m / 44330.0), 5.255)

def moving_average_list(seq, window):
    out = []
    acc = 0.0
    for i, v in enumerate(seq):
        acc += v
        if i >= window: acc -= seq[i-window]
        denom = window if i >= window-1 else (i+1)
        out.append(acc/denom)
    return out

# ───── DPS310 setup (real sensor only) ─────
_OVERSAMPLE_MAP = {0:"x1",1:"x2",2:"x4",3:"x8",4:"x16",5:"x32",6:"x64",7:"x128"}
_RATE_MAP = {0:1,1:2,2:4,3:8,4:16,5:32,6:64,7:128}

def _read_cfg_str(sensor):
    try:
        p_osr = getattr(sensor, "pressure_oversample_count", "n/a")
        t_osr = getattr(sensor, "temperature_oversample_count", "n/a")
        p_rate = getattr(sensor, "pressure_rate", "n/a")
        t_rate = getattr(sensor, "temperature_rate", getattr(sensor, "pressure_rate", "n/a"))
        def fmt_osr(v):
            try: return f"{_OVERSAMPLE_MAP.get(int(v), str(v))} (raw {int(v)})"
            except Exception: return str(v)
        def fmt_rate(v):
            try: return f"{_RATE_MAP.get(int(v), str(v))} Hz (raw {int(v)})"
            except Exception: return str(v)
        return (f"Sensor: DPS310\n"
                f"  Pressure OSR: {fmt_osr(p_osr)}\n"
                f"  Temperature OSR: {fmt_osr(t_osr)}\n"
                f"  Pressure Rate: {fmt_rate(p_rate)}\n"
                f"  Temperature Rate: {fmt_rate(t_rate)}")
    except Exception as e:
        return f"Sensor: DPS310 (cfg read error: {e})"

def _force_high_precision(sensor):
    # Prefer library constants; otherwise use indices (7,2,6).
    def _const(name_list):
        for nm in name_list:
            if hasattr(adafruit_dps310, nm):
                return getattr(adafruit_dps310, nm)
        return None
    P_OSR_CONST = _const(["OVERSAMPLE_X128","OVERSAMPLE_128","OSR_128","OVERSAMPLE_7"])
    T_OSR_CONST = _const(["OVERSAMPLE_X4","OVERSAMPLE_4","OSR_4","OVERSAMPLE_2"])
    RATE_CONST  = _const(["RATE_64_HZ","RATE_64HZ","RATE_64"])

    setattr(sensor, "pressure_oversample_count", P_OSR_CONST if P_OSR_CONST is not None else 7)
    setattr(sensor, "temperature_oversample_count", T_OSR_CONST if T_OSR_CONST is not None else 2)
    setattr(sensor, "pressure_rate", RATE_CONST if RATE_CONST is not None else 6)
    setattr(sensor, "temperature_rate", RATE_CONST if RATE_CONST is not None else 6)

def init_dps310():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_dps310.DPS310(i2c)
    _force_high_precision(sensor)
    return sensor

def get_sensor_readings(sensor):
    # Real reads; no simulation fallback
    p = float(sensor.pressure)      # hPa
    t = float(sensor.temperature)   # °C
    return p, t

# ───── Optional: try syncing system clock from RTC (if installed) ─────
def maybe_sync_from_rtc(max_diff=5.0):
    info = {"action": "none"}
    try:
        if adafruit_ds3231 is None:
            return info
        i2c = busio.I2C(board.SCL, board.SDA)
        rtc_dev = adafruit_ds3231.DS3231(i2c)
        rtc = rtc_dev.datetime  # time.struct_time
        # Convert to ISO string for 'date -s'; adjust to local timezone via system default
        datestr = f"{rtc.tm_year:04d}-{rtc.tm_mon:02d}-{rtc.tm_mday:02d} {rtc.tm_hour:02d}:{rtc.tm_min:02d}:{rtc.tm_sec:02d}"
        # Only set if off by more than threshold
        import subprocess, datetime as _dt
        sys_now = _dt.datetime.now()
        rtc_dt = _dt.datetime(rtc.tm_year, rtc.tm_mon, rtc.tm_mday, rtc.tm_hour, rtc.tm_min, rtc.tm_sec)
        if abs((sys_now - rtc_dt).total_seconds()) > max_diff:
            r = subprocess.run(["sudo", "date", "-s", datestr], capture_output=True, text=True)
            info["action"] = "system_clock_set_from_rtc"
            info["returncode"] = r.returncode
    except Exception as e:
        info["action"] = f"error: {e}"
    return info

time_sync_report = maybe_sync_from_rtc()

# ───── UI setup ─────
root = tk.Tk()
root.title(VERSION_STRING)
root.geometry("700x600+0+0")
root.configure(bg=ROOT_BG)

menubar = tk.Menu(root)

# DSP menu
dsp_menu = tk.Menu(menubar, tearoff=0)
def _set_smoothing_window():
    global SMOOTH_WINDOW
    from tkinter import simpledialog
    prompt = f"Enter window size (samples) [current: {SMOOTH_WINDOW}, default: 10]:"
    val = simpledialog.askinteger("Smoothing window", prompt,
                                  minvalue=1, maxvalue=600,
                                  initialvalue=SMOOTH_WINDOW)
    if val:
        SMOOTH_WINDOW = int(val)
dsp_menu.add_command(label="Smoothing window...", command=_set_smoothing_window)
menubar.add_cascade(label="DSP", menu=dsp_menu)

# Sensor menu
sensor_menu = tk.Menu(menubar, tearoff=0)

def sensor_info():
    info = _read_cfg_str(dps) if dps is not None else "Sensor not detected."
    help_text = (
        "\n\nNotes:\n"
        "• OSR (Oversampling): averages multiple conversions in silicon.\n"
        "• Rate (Hz): conversions per second.\n"
        "• High-precision profile here: P OSR x128, T OSR x4, rates 64 Hz."
    )
    messagebox.showinfo("Sensor Information", info + help_text)

def sensor_redetect():
    global dps
    try:
        dps = init_dps310()
        messagebox.showinfo("Sensor Re-detect", _read_cfg_str(dps))
    except Exception as e:
        messagebox.showerror("Sensor Re-detect", f"Failed to initialize DPS310:\n{e}")

def sensor_force_hp():
    global dps
    try:
        _force_high_precision(dps)
        messagebox.showinfo("High-Precision", _read_cfg_str(dps))
    except Exception as e:
        messagebox.showerror("High-Precision", f"Failed to set high-precision:\n{e}")

sensor_menu.add_command(label="Sensor Info…", command=sensor_info)
sensor_menu.add_command(label="Re-detect Sensor", command=sensor_redetect)
sensor_menu.add_command(label="Force High-Precision Now", command=sensor_force_hp)
menubar.add_cascade(label="Sensor", menu=sensor_menu)

root.config(menu=menubar)

# Layout containers
main = tk.Frame(root, bg=ROOT_BG, padx=16, pady=12)
main.pack(fill="both", expand=True)
main.grid_columnconfigure(0, weight=1)
main.grid_columnconfigure(1, weight=1)

# Top info row
top = tk.Frame(main, bg=ROOT_BG)
top.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 8))
top.grid_columnconfigure(0, weight=1)
top.grid_columnconfigure(1, weight=1)

L = tk.Frame(top, bg=ROOT_BG); L.grid(row=0, column=0, sticky="nw")
abs_hpa = tk.Label(L, text="Absolute (hPa): --", font=HEADER, bg=ROOT_BG, fg="red", anchor="w");  abs_hpa.grid(row=0, column=0, sticky="w")
abs_inhg = tk.Label(L, text="Absolute (inHg): --", font=DATA,   bg=ROOT_BG, anchor="w");  abs_inhg.grid(row=1, column=0, sticky="w")
noaa_label = tk.Label(L, text="NOAA Smoothed (hPa): --", font=DATA, bg=ROOT_BG, fg="green", anchor="w"); noaa_label.grid(row=2, column=0, sticky="w")
sm_lbl   = tk.Label(L, text="Smoothed (hPa): --", font=DATA,   bg=ROOT_BG, fg="blue", anchor="w");  sm_lbl.grid(row=3, column=0, sticky="w")
tr_lbl   = tk.Label(L, text="Trend (hPa/min): --", font=DATA, bg=ROOT_BG, anchor="w");  tr_lbl.grid(row=4, column=0, sticky="w")
nz_lbl   = tk.Label(L, text="Noise (hPa RMS): --", font=DATA, bg=ROOT_BG, anchor="w");  nz_lbl.grid(row=5, column=0, sticky="w")

R = tk.Frame(top, bg=ROOT_BG); R.grid(row=0, column=1, sticky="ne", padx=(16,0))
rel_hpa = tk.Label(R, text="Relative (hPa): --", font=HEADER, bg=ROOT_BG, anchor="w"); rel_hpa.grid(row=0, column=0, sticky="w")
rel_inhg = tk.Label(R, text="Relative (inHg): --", font=DATA,   bg=ROOT_BG, anchor="w"); rel_inhg.grid(row=1, column=0, sticky="w")
alt_row = tk.Frame(R, bg=ROOT_BG); alt_row.grid(row=2, column=0, sticky="w", pady=(5,0))
tk.Label(alt_row, text="Reference Altitude (ft):", font=DATA, bg=ROOT_BG, anchor="w").grid(row=0, column=0, sticky="w")
alt_var = tk.StringVar(value="1132"); tk.Entry(alt_row, textvariable=alt_var, width=8, font=DATA).grid(row=0, column=1, sticky="w", padx=(5,0))

# Two info lines above buttons
info_frame = tk.Frame(main, bg=ROOT_BG)
info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6,4))
info_frame.grid_columnconfigure(0, weight=1)
info_frame.grid_columnconfigure(1, weight=1)
t_f = tk.Label(info_frame, text="--", font=DATA, bg=ROOT_BG, anchor="w"); t_f.grid(row=0, column=0, sticky="w")
log_lbl = tk.Label(info_frame, text="Log file: --", font=DATA, bg=ROOT_BG, anchor="w"); log_lbl.grid(row=0, column=1, sticky="e")
upt = tk.Label(info_frame, text="Uptime: 00:00:00:00", font=DATA, bg=ROOT_BG, anchor="w"); upt.grid(row=1, column=0, sticky="w")
dtl = tk.Label(info_frame, text="Date/Time: --", font=DATA, bg=ROOT_BG, anchor="e"); dtl.grid(row=1, column=1, sticky="e")

# Button row — Capture only
btnrow = tk.Frame(main, bg=ROOT_BG)
btnrow.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6,6))
btnrow.grid_columnconfigure(0, weight=1)

def _screencap_path():
    scr_dir = os.path.join(os.path.expanduser("~"), "blinka-test", "Screens")
    os.makedirs(scr_dir, exist_ok=True)
    return os.path.join(scr_dir, "screencap_" + datetime.now().strftime("%Y%m%d_%H-%M-%S") + ".png")

def on_capture():
    out = _screencap_path()
    ok = False
    try:
        win_id = str(root.winfo_id())
        r = subprocess.run(["import", "-window", win_id, out], capture_output=True, text=True)
        ok = (r.returncode == 0 and os.path.exists(out))
    except Exception:
        ok = False
    if not ok and shutil.which("scrot"):
        try:
            r = subprocess.run(["scrot", "--focused", out], capture_output=True, text=True)
            ok = (r.returncode == 0 and os.path.exists(out))
        except Exception:
            ok = False
    messagebox.showinfo("Capture", f"Saved: {out}" if ok else "Capture failed. Install 'imagemagick' or 'scrot'.")

tk.Button(btnrow, text="Capture", font=DATA, command=on_capture).grid(row=0, column=0, sticky="ew", padx=4)

# Bottom plot
plot_frame = tk.Frame(main, bg=ROOT_BG)
plot_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
main.grid_rowconfigure(3, weight=1)

plot_label = tk.Label(plot_frame, text=" ", font=LABELF, bg=ROOT_BG, anchor="w")
plot_label.pack(anchor="w")
canvas = tk.Canvas(plot_frame, height=300, bg="white", highlightthickness=1, highlightbackground="black")
canvas.pack(fill="both", expand=True)

def format_hpa_label(data):
    if not data: return ""
    dmin = min(data); dmax = max(data); dchg = dmax - dmin
    return f"H {dmax:.3f} hPa, L {dmin:.3f} hPa, ΔhPa: {dchg:.3f}"

def draw_strip():
    # 1 px = 1 sample, grow from left to right, scroll when full
    canvas.delete("all")
    w = max(canvas.winfo_width(), 10); h = max(canvas.winfo_height(), 10)
    # Grid ticks each 60 px
    for x in range(0, w, 60):
        canvas.create_line(x, 0, x, h-1, fill="#cfd8dc")

    n = len(STRIP_HISTORY)
    plot_label.config(text=format_hpa_label(STRIP_HISTORY))
    if n < 2: return

    if n >= w:
        src = STRIP_HISTORY[-w:]
        xs = list(range(w))
    else:
        src = STRIP_HISTORY
        xs = list(range(n))

    pmin = min(src); pmax = max(src); span = max(pmax - pmin, 1e-12)

    # Blue MA (user window)
    ma_n = max(1, min(SMOOTH_WINDOW, len(src)))
    blue = moving_average_list(src, ma_n)

    # Green NOAA (fixed 60-sample mean)
    noaa = moving_average_list(src, min(NOAA_SMOOTH_N, len(src)))

    raw_pts, blue_pts, green_pts = [], [], []
    for x, vr, vb, vg in zip(xs, src, blue, noaa):
        y_r = h - 1 - ((vr - pmin)/span)*(h-1)
        y_b = h - 1 - ((vb - pmin)/span)*(h-1)
        y_g = h - 1 - ((vg - pmin)/span)*(h-1)
        raw_pts.extend((x, y_r))
        blue_pts.extend((x, y_b))
        green_pts.extend((x, y_g))

    if len(raw_pts)   >= 4: canvas.create_line(raw_pts,   fill="red")
    if len(blue_pts)  >= 4: canvas.create_line(blue_pts,  fill="blue")
    if len(green_pts) >= 4: canvas.create_line(green_pts, fill="green")

# ───── Logging ─────
os.makedirs("DataLogs", exist_ok=True)
log_path = os.path.join("DataLogs", f"{PROGRAM_ID}_{datetime.now().strftime('%Y%m%d')}.csv")
is_new = not os.path.exists(log_path)
logfile = open(log_path, "a", newline="")
writer = csv.writer(logfile)
if is_new:
    logfile.write(f"# Program ID: {PROGRAM_ID}\n")
    logfile.write(f"# Version: {VERSION_STRING}\n")
    if time_sync_report.get("action") != "none":
        logfile.write(f"# Time Sync: {time_sync_report}\n")
    writer.writerow(["local_hms","sample_seq","abs_hPa","rel_hPa","abs_inHg","rel_inHg","temp_C","temp_F"])
    logfile.flush()

# ───── Initialize sensor (required) ─────
try:
    dps = init_dps310()
except Exception as e:
    messagebox.showerror("DPS310 Error", f"Failed to initialize DPS310:\n{e}\n\nThis build has no simulator fallback. Exiting.")
    sys.exit(1)

# ───── Main loop ─────
sample_seq = 0
t_high_f = t_low_f = None
start_time = time.time()

def update():
    global sample_seq, t_high_f, t_low_f
    now = datetime.now()

    try:
        abs_h, tC = get_sensor_readings(dps)
    except Exception as e:
        messagebox.showerror("DPS310 Read Error", f"Failed to read DPS310:\n{e}")
        # Do not simulate; just schedule another attempt
        root.after(int(SAMPLE_INTERVAL*1000), update)
        return

    tF = c_to_f(tC); abs_in = hpa_to_inhg(abs_h)

    # relative (sea-level) using reference altitude
    try: alt_ft = float(alt_var.get())
    except Exception: alt_ft = 1132.0
    rel_h = sea_level_pressure_hpa(abs_h, alt_ft*0.3048)
    rel_in = hpa_to_inhg(rel_h)

    # buffers + history
    buf_1min.append(abs_h)
    STRIP_HISTORY.append(abs_h)
    if len(STRIP_HISTORY) > 20000: del STRIP_HISTORY[:-20000]

    # temp stats
    if t_high_f is None or tF > t_high_f: t_high_f = tF
    if t_low_f  is None or tF < t_low_f:  t_low_f  = tF

    # labels
    abs_hpa.config(text=f"Absolute (hPa): {abs_h:7.3f}")
    abs_inhg.config(text=f"Absolute (inHg): {abs_in:6.3f}")
    ma_n = max(1, min(SMOOTH_WINDOW, len(STRIP_HISTORY)))
    sm_val = sum(STRIP_HISTORY[-ma_n:])/ma_n if STRIP_HISTORY else None
    sm_lbl.config(text=("Smoothed (hPa): " + (f"{sm_val:.3f}" if sm_val is not None else "--")))
    # NOAA label
    n60 = min(NOAA_SMOOTH_N, len(STRIP_HISTORY))
    noaa_val = sum(STRIP_HISTORY[-n60:])/n60 if n60 > 0 else None
    noaa_label.config(text=("NOAA Smoothed (hPa): " + (f"{noaa_val:.3f}" if noaa_val is not None else "--")))

    rel_hpa.config(text=f"Relative (hPa): {rel_h:7.3f}")
    rel_inhg.config(text=f"Relative (inHg): {rel_in:6.3f}")

    # Trend and noise based on last 60s
    if len(buf_1min) >= 2:
        y = list(buf_1min); N = len(y)
        x = list(range(N))
        mx = sum(x)/N; my = sum(y)/N
        num = sum((x[i]-mx)*(y[i]-my) for i in range(N))
        den = sum((x[i]-mx)**2 for i in range(N)) or 1.0
        slope_per_s = num/den
        tr_lbl.config(text=f"Trend (hPa/min): {slope_per_s*60.0:+.3f}")
        avg = my
        nz = (sum((v-avg)**2 for v in y)/N) ** 0.5
        nz_lbl.config(text=f"Noise (hPa RMS): {nz:.3f}")
    else:
        tr_lbl.config(text="Trend (hPa/min): --")
        nz_lbl.config(text="Noise (hPa RMS): --")

    # Bottom text lines
    def fmt_f(v): return ("--" if v is None else f"{v:0.1f}°F")
    t_f.config(text=f"{tF:0.1f}°F,  H {fmt_f(t_high_f)},  L {fmt_f(t_low_f)}")
    def fmt_uptime(s): t=int(s); d=t//86400; r=t%86400; h=r//3600; r%=3600; m=r//60; sec=r%60; return f"{d:02d}:{h:02d}:{m:02d}:{sec:02d}"
    uptime_s = time.time() - start_time
    upt.config(text=f"Uptime: {fmt_uptime(uptime_s)}")
    log_lbl.config(text=f"Log file: {log_path}")
    dtl.config(text=f"Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # Draw plot
    draw_strip()

    # Log
    sample_seq += 1
    writer.writerow([now.strftime("%H:%M:%S"), sample_seq,
                     f"{abs_h:.3f}", f"{rel_h:.3f}", f"{abs_in:.4f}", f"{rel_in:.4f}",
                     f"{tC:.3f}", f"{tF:.3f}"])
    logfile.flush()

    root.after(int(SAMPLE_INTERVAL*1000), update)

# ───── Initialize sensor (required) ─────
try:
    dps = init_dps310()
except Exception as e:
    messagebox.showerror("DPS310 Error", f"Failed to initialize DPS310:\n{e}\n\nThis build has no simulator fallback. Exiting.")
    sys.exit(1)

# Start
root.after(1000, update)
root.mainloop()
