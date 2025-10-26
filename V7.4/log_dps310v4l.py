import time
import csv
import datetime
import board
import busio
import adafruit_dps310
import tkinter as tk
import tkinter.ttk as ttk
import signal
import sys
import math

#
# Helper conversion functions
#

def c_to_f(c):
    # °F = (°C * 9/5) + 32
    return (c * 9.0 / 5.0) + 32.0

def hpa_to_inhg(hpa):
    # 1 inHg = 33.8638866667 hPa
    return hpa / 33.8638866667


#
# Sensor + CSV setup
#

# Initialize I2C and DPS310 sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_dps310.DPS310(i2c)

# ---------- HIGH RES / LOW NOISE TRY BLOCKS ----------
try:
    sensor.pressure_oversample_count = 128
except Exception as e:
    print("pressure_oversample_count config skipped:", e)

try:
    sensor.temperature_oversample_count = 128
except Exception as e:
    print("temperature_oversample_count config skipped:", e)

try:
    sensor.pressure_rate = 1  # 1 sample/sec
except Exception as e:
    print("pressure_rate config skipped:", e)

try:
    sensor.temperature_rate = 1  # 1 sample/sec
except Exception as e:
    print("temperature_rate config skipped:", e)

# Attempt to set continuous measurement mode for both temp & pressure
set_mode_ok = False
for candidate in (
    "CONTINUOUS",
    "continuous",
    2,
):
    if set_mode_ok:
        break
    try:
        setattr(sensor, "mode", getattr(adafruit_dps310, candidate))
        set_mode_ok = True
    except Exception:
        try:
            sensor.mode = candidate
            set_mode_ok = True
        except Exception:
            pass

# ---------- END CONFIG SECTION ----------

# Open CSV file for writing (overwrite each run)
logfile = open("dps310_log.csv", "w", newline="")
writer = csv.writer(logfile)

# Human-readable header block (commented)
logfile.write("# DPS310 Pressure Logger\n")
logfile.write("# timestamp_iso8601_utc      : UTC time of sample (ISO 8601)\n")
logfile.write("# temp_C                     : Sensor temperature in degrees C\n")
logfile.write("# temp_F                     : Sensor temperature in degrees F\n")
logfile.write("# pressure_hPa               : Raw pressure in hPa from DPS310\n")
logfile.write("# pressure_inHg              : Pressure converted to inches of mercury\n")
logfile.write("# smooth_hPa_30s_avg         : Moving-average pressure over last ~30s\n")
logfile.write("# trend_hPa_per_min          : Pressure change rate (hPa/min) over ~1 min\n")
logfile.write("# noise_hPa_RMS_30s          : RMS noise (std dev) of pressure over last ~30s\n")
logfile.write("# \n")

# Machine-readable column header row
writer.writerow([
    "timestamp_iso8601_utc",
    "temp_C",
    "temp_F",
    "pressure_hPa",
    "pressure_inHg",
    "smooth_hPa_30s_avg",
    "trend_hPa_per_min",
    "noise_hPa_RMS_30s"
])
logfile.flush()

#
# Data buffers for analysis and visualization
#
# We maintain four rolling buffers, all updated once per second:
#   ~60   seconds   (1 minute)
#   ~600  seconds   (10 minutes)
#   ~3600 seconds   (1 hour)
#   ~43200 seconds  (12 hours)
#
pressure_buffer_60 = []       # short term (wiggles)
pressure_buffer_600 = []      # 10 minutes
pressure_buffer_3600 = []     # 1 hour
pressure_buffer_43200 = []    # 12 hours

# We'll still compute smoothing / noise / trend from the 60-second buffer.
SMOOTH_WINDOW = 30            # samples (~30s) for smoothing & noise RMS
ANALYSIS_WINDOW = 60          # samples (~60s) used for trend calc

# Sparkline canvas size
SPARK_WIDTH = 200
SPARK_HEIGHT = 60

#
# Graceful shutdown handling
#

running = True

def handle_close():
    """Stop update loop and close window."""
    global running
    running = False
    root.destroy()

def handle_sigint(sig, frame):
    """Handle Ctrl+C."""
    handle_close()

signal.signal(signal.SIGINT, handle_sigint)

#
# GUI setup
#

root = tk.Tk()
root.title("Pressure V7.4")

mainframe = ttk.Frame(root, padding=20)
mainframe.grid(row=0, column=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Row layout now becomes:
#  0  Pressure (hPa)
#  1  Smoothed (hPa)
#  2  Trend (hPa/min)
#  3  Noise (hPa RMS)
#  4  Last 60s sparkline
#  5  Last 600s sparkline
#  6  Last 1 hr sparkline
#  7  Last 12 hr sparkline
#  8  Pressure (inHg)
#  9  Temperature (°C)
# 10  Temperature (°F)
# 11  Timestamp

# Row 0: Pressure hPa (raw)
ttk.Label(mainframe, text="Pressure (hPa):", font=("Arial", 12)).grid(
    row=0, column=0, sticky="e", padx=(0,10), pady=5
)
press_hpa_value = ttk.Label(mainframe, text="----.---", font=("Consolas", 14))
press_hpa_value.grid(row=0, column=1, sticky="w", pady=5)

# Row 1: Smoothed pressure (moving average)
ttk.Label(mainframe, text="Smoothed (hPa):", font=("Arial", 12)).grid(
    row=1, column=0, sticky="e", padx=(0,10), pady=5
)
smooth_hpa_value = ttk.Label(mainframe, text="----.---", font=("Consolas", 14))
smooth_hpa_value.grid(row=1, column=1, sticky="w", pady=5)

# Row 2: Trend ~1 min
ttk.Label(mainframe, text="Trend (hPa/min):", font=("Arial", 12)).grid(
    row=2, column=0, sticky="e", padx=(0,10), pady=5
)
trend_value = ttk.Label(mainframe, text="+0.000", font=("Consolas", 14))
trend_value.grid(row=2, column=1, sticky="w", pady=5)

# Row 3: Noise (RMS of last ~30s)
ttk.Label(mainframe, text="Noise (hPa RMS):", font=("Arial", 12)).grid(
    row=3, column=0, sticky="e", padx=(0,10), pady=5
)
noise_value = ttk.Label(mainframe, text="0.000", font=("Consolas", 14))
noise_value.grid(row=3, column=1, sticky="w", pady=5)

# Row 4: Sparkline 60 s
ttk.Label(mainframe, text="Last 60s (hPa):", font=("Arial", 12)).grid(
    row=4, column=0, sticky="e", padx=(0,10), pady=5
)
spark_canvas_60 = tk.Canvas(
    mainframe,
    width=SPARK_WIDTH,
    height=SPARK_HEIGHT,
    bg="white",
    highlightthickness=1,
    highlightbackground="black"
)
spark_canvas_60.grid(row=4, column=1, sticky="w", pady=5)

# Row 5: Sparkline 600 s (10 min)
ttk.Label(mainframe, text="Last 600s (hPa):", font=("Arial", 12)).grid(
    row=5, column=0, sticky="e", padx=(0,10), pady=5
)
spark_canvas_600 = tk.Canvas(
    mainframe,
    width=SPARK_WIDTH,
    height=SPARK_HEIGHT,
    bg="white",
    highlightthickness=1,
    highlightbackground="black"
)
spark_canvas_600.grid(row=5, column=1, sticky="w", pady=5)

# Row 6: Sparkline 1 hr (3600 s)
ttk.Label(mainframe, text="Last 1 hr (hPa):", font=("Arial", 12)).grid(
    row=6, column=0, sticky="e", padx=(0,10), pady=5
)
spark_canvas_3600 = tk.Canvas(
    mainframe,
    width=SPARK_WIDTH,
    height=SPARK_HEIGHT,
    bg="white",
    highlightthickness=1,
    highlightbackground="black"
)
spark_canvas_3600.grid(row=6, column=1, sticky="w", pady=5)

# Row 7: Sparkline 12 hr (43200 s)
ttk.Label(mainframe, text="Last 12 hr (hPa):", font=("Arial", 12)).grid(
    row=7, column=0, sticky="e", padx=(0,10), pady=5
)
spark_canvas_43200 = tk.Canvas(
    mainframe,
    width=SPARK_WIDTH,
    height=SPARK_HEIGHT,
    bg="white",
    highlightthickness=1,
    highlightbackground="black"
)
spark_canvas_43200.grid(row=7, column=1, sticky="w", pady=5)

# Row 8: Pressure inHg
ttk.Label(mainframe, text="Pressure (inHg):", font=("Arial", 12)).grid(
    row=8, column=0, sticky="e", padx=(0,10), pady=5
)
press_inhg_value = ttk.Label(mainframe, text="--.--", font=("Consolas", 14))
press_inhg_value.grid(row=8, column=1, sticky="w", pady=5)

# Row 9: Temperature (°C)
ttk.Label(mainframe, text="Temperature (°C):", font=("Arial", 12)).grid(
    row=9, column=0, sticky="e", padx=(0,10), pady=5
)
temp_c_value = ttk.Label(mainframe, text="--.--", font=("Consolas", 14))
temp_c_value.grid(row=9, column=1, sticky="w", pady=5)

# Row 10: Temperature (°F)
ttk.Label(mainframe, text="Temperature (°F):", font=("Arial", 12)).grid(
    row=10, column=0, sticky="e", padx=(0,10), pady=5
)
temp_f_value = ttk.Label(mainframe, text="--.--", font=("Consolas", 14))
temp_f_value.grid(row=10, column=1, sticky="w", pady=5)

# Row 11: Timestamp / status
status_label = ttk.Label(mainframe, text="Timestamp: --", font=("Arial", 10))
status_label.grid(row=11, column=0, columnspan=2, pady=(15,0))


#
# Sparkline drawing helpers
#

def draw_sparkline(canvas, data_list):
    """
    Draw scaled line plot of data_list on canvas.
    Oldest -> left, newest -> right.
    Auto-scales Y to min/max of that list.
    """
    canvas.delete("all")

    n = len(data_list)
    if n < 2:
        return

    pmin = min(data_list)
    pmax = max(data_list)
    span = pmax - pmin
    if span <= 0:
        span = 1e-9  # avoid div-by-zero on flat data

    pts = []
    for x in range(SPARK_WIDTH):
        # map pixel column -> sample index
        src_idx_float = (x / (SPARK_WIDTH - 1)) * (n - 1)
        src_idx = int(round(src_idx_float))
        if src_idx < 0:
            src_idx = 0
        if src_idx > n - 1:
            src_idx = n - 1

        p = data_list[src_idx]

        norm = (p - pmin) / span        # 0 at min, 1 at max
        y = SPARK_HEIGHT - 1 - norm * (SPARK_HEIGHT - 1)

        pts.append((x, y))

    flat = []
    for (xp, yp) in pts:
        flat.extend((xp, yp))

    canvas.create_line(flat)

def update_all_sparklines():
    draw_sparkline(spark_canvas_60,     pressure_buffer_60)
    draw_sparkline(spark_canvas_600,    pressure_buffer_600)
    draw_sparkline(spark_canvas_3600,   pressure_buffer_3600)
    draw_sparkline(spark_canvas_43200,  pressure_buffer_43200)


#
# Stats computation
#

def compute_stats_and_update_buffers(current_pressure_hpa):
    """
    Push current_pressure_hpa into all buffers, trim them,
    and compute:
      smoothed_hpa      : avg of last ~30s from 60s buffer
      trend_hpa_per_min : slope over ~60s buffer
      noise_rms_hpa     : RMS deviation of last ~30s
    Returns (smoothed_hpa, trend_hpa_per_min, noise_rms_hpa)
    """

    # --- Update 60s buffer ---
    pressure_buffer_60.append(current_pressure_hpa)
    if len(pressure_buffer_60) > 60:  # keep ~60 seconds
        del pressure_buffer_60[0:len(pressure_buffer_60)-60]

    # --- Update 600s buffer (~10 min) ---
    pressure_buffer_600.append(current_pressure_hpa)
    if len(pressure_buffer_600) > 600:
        del pressure_buffer_600[0:len(pressure_buffer_600)-600]

    # --- Update 3600s buffer (~1 hr) ---
    pressure_buffer_3600.append(current_pressure_hpa)
    if len(pressure_buffer_3600) > 3600:
        del pressure_buffer_3600[0:len(pressure_buffer_3600)-3600]

    # --- Update 43200s buffer (~12 hr) ---
    pressure_buffer_43200.append(current_pressure_hpa)
    if len(pressure_buffer_43200) > 43200:
        del pressure_buffer_43200[0:len(pressure_buffer_43200)-43200]

    # ---- Compute smoothed (30s avg) and noise RMS (30s std dev) ----
    if len(pressure_buffer_60) >= 1:
        last_slice = pressure_buffer_60[-SMOOTH_WINDOW:]
        smoothed_hpa = sum(last_slice) / len(last_slice)

        if len(last_slice) > 1:
            accum = 0.0
            for v in last_slice:
                diff = v - smoothed_hpa
                accum += diff * diff
            variance = accum / len(last_slice)
            noise_rms_hpa = math.sqrt(variance)
        else:
            noise_rms_hpa = float("nan")
    else:
        smoothed_hpa = float("nan")
        noise_rms_hpa = float("nan")

    # ---- Trend hPa/min using ~60s buffer ----
    if len(pressure_buffer_60) >= 2:
        oldest = pressure_buffer_60[0]
        newest = pressure_buffer_60[-1]
        seconds_span = len(pressure_buffer_60) - 1  # ~1 sec/sample
        if seconds_span > 0:
            trend_hpa_per_min = (newest - oldest) * (60.0 / seconds_span)
        else:
            trend_hpa_per_min = 0.0
    else:
        trend_hpa_per_min = 0.0

    return smoothed_hpa, trend_hpa_per_min, noise_rms_hpa


#
# Update loop
#

def update_readings():
    """Read sensor, update GUI, log to CSV, update sparklines every second."""
    if not running:
        return

    try:
        # Read sensor
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        temp_c = sensor.temperature          # °C
        pres_hpa = sensor.pressure           # hPa

        # Convert units
        temp_f = c_to_f(temp_c)              # °F
        pres_inhg = hpa_to_inhg(pres_hpa)    # inHg

        # Update buffers + compute derived stats
        smoothed_hpa, trend_hpa_per_min, noise_rms_hpa = (
            compute_stats_and_update_buffers(pres_hpa)
        )

        # GUI numeric fields
        press_hpa_value.config(text=f"{pres_hpa:.3f}")

        if math.isnan(smoothed_hpa):
            smooth_hpa_value.config(text="----.---")
        else:
            smooth_hpa_value.config(text=f"{smoothed_hpa:.3f}")

        trend_value.config(text=f"{trend_hpa_per_min:+.3f}")

        if math.isnan(noise_rms_hpa):
            noise_value.config(text="----")
        else:
            noise_value.config(text=f"{noise_rms_hpa:.3f}")

        press_inhg_value.config(text=f"{pres_inhg:.3f}")

        temp_c_value.config(text=f"{temp_c:.2f}")
        temp_f_value.config(text=f"{temp_f:.2f}")
        status_label.config(text=f"Timestamp (UTC): {now}")

        # Update all 4 sparklines
        update_all_sparklines()

        # Prepare CSV strings (handle NaN gracefully)
        smooth_csv = "" if math.isnan(smoothed_hpa) else f"{smoothed_hpa:.3f}"
        trend_csv  = f"{trend_hpa_per_min:.3f}"
        noise_csv  = "" if math.isnan(noise_rms_hpa) else f"{noise_rms_hpa:.3f}"

        # CSV row
        writer.writerow([
            now,
            f"{temp_c:.3f}",
            f"{temp_f:.3f}",
            f"{pres_hpa:.3f}",
            f"{pres_inhg:.4f}",
            smooth_csv,
            trend_csv,
            noise_csv
        ])
        logfile.flush()

    except Exception as e:
        status_label.config(text=f"ERROR: {e}")

    # Loop again in 1 second
    root.after(1000, update_readings)

# Schedule first update
root.after(0, update_readings)

# Close handler
root.protocol("WM_DELETE_WINDOW", handle_close)

# Tk main loop
root.mainloop()

# Cleanup
logfile.close()
print("Stopped logging and closed CSV.")
sys.exit(0)
