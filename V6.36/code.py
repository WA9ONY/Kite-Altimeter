# Kite Altimeter
# Version:
VERSION = 6.35
VERSION_string = "V"+str(VERSION)
# Date: 2025-07-27
# Author: David Haworth, WA9ONY
# Website: https://www.qrz.com/db/WA9ONY
# GitHub https://github.com/WA9ONY/Adafruit-Feather/tree/main

# ----------------------------------------------------
# Kite Altimeter Hardware
# ----------------------------------------------------
# - Adafruit Feather RP2040 Adalogger - 8MB Flash with microSD Card - STEMMA QT / Qwiic
#     https://www.adafruit.com/product/5980
# - SanDisk 32GB MAX Endurance microSDHC Card with Adapter for Home Security Cameras and Dash cams -
#   - C10, U3, V30, 4K UHD, Micro SD Card - SDSQQVR-032G-GN6IA
#   - Amazon  
# - Lithium Ion Polymer Battery - 3.7V 500mAh
#     https://www.adafruit.com/product/1578
#     Adalogger runs for ~5 hours 
# - Adafruit Monochrome 1.12" 128x128 OLED Graphic Display - STEMMA QT / Qwiic
#     https://www.adafruit.com/product/5297
# - Adafruit DPS310 Precision Barometric Pressure / Altitude Sensor
#     https://www.adafruit.com/product/4494
# - Adafruit DS3231 Precision RTC - STEMMA QT + SD
#     https://www.adafruit.com/product/5188
# - Adafruit 9-DOF Absolute Orientation IMU Fusion Breakout - BNO055 - STEMMA QT / Qwiic
#     https://www.adafruit.com/product/4646
# - SparkFun Air Velocity Sensor Breakout - FS3000-1005 (Qwiic)
#     https://www.sparkfun.com/sparkfun-air-velocity-sensor-breakout-fs3000-1005-qwiic.html
# - Three Adafruit STEMMA QT / Qwiic JST SH 4-Pin Cable - 50mm Long
#     https://www.adafruit.com/product/4399
# - Two Adafruit STEMMA QT / Qwiic JST SH 4-Pin Cable - 100mm Long
#     https://www.adafruit.com/product/4210
# - Pill container
#
# ----------------------------------------------------
# Development Tools
# ----------------------------------------------------
# - Raspberry Pi 500 Rev 1.0 computer
# - OS: Debian GNU/Linux 12 (bookworm) aarch64 
# - Thonny IDE Version 4.1.4 Comes with Raspberry OS install. https://thonny.org/
# - Circup (for managing CircuitPython libraries) https://github.com/adafruit/circup
# - Circup is a Terminal CLI tool to install and update CircuitPython and libraries on the microcontroller board.

# ----------------------------------------------------
# CircuitPython and Libraries
# ----------------------------------------------------
# - CircuitPython 9.2.6 https://circuitpython.org/board/adafruit_feather_rp2040/
# - CircuitPython 9.X Libraries https://circuitpython.org/libraries


# ----------------------------------------------------
# Modules and Libraries
# ----------------------------------------------------
import os
import gc
import sys
import math
import time
import alarm
import board
import busio
import storage
import analogio
import neopixel
import digitalio
import displayio
import adafruit_sdcard
import microcontroller
import adafruit_ds3231
import adafruit_dps310 # Advanced
#from fs3000 import FS3000_1005
from fs3000 import FS3000_1015
import adafruit_bno055
from adafruit_bno055 import (
    BNO055_I2C,
    AXIS_REMAP_X, AXIS_REMAP_Y, AXIS_REMAP_Z,
    AXIS_REMAP_POSITIVE, AXIS_REMAP_NEGATIVE,
    CONFIG_MODE, NDOF_MODE
)

import terminalio
from adafruit_display_text import bitmap_label as label
from i2cdisplaybus import I2CDisplayBus
from adafruit_displayio_sh1107 import SH1107, DISPLAY_OFFSET_ADAFRUIT_128x128_OLED_5297

#from collections import deque

# ----------------------------------------------------
# Global Variables and Constants
# ----------------------------------------------------

SUMMARY_PRINT  = True 	# Print summary for flying
WIND_PRINT = False 		# Print wind details

DEBUG = True   # True and False
DEBUG1 = False # Print full altitude to SD card
DEBUG2 = False  # Print alt H, N, L, Bat
DEBUG3 = False # Simular to DEBUG1
BNO_CAL_PRINT = True # Print BNO055 calibration process at startup

# --- BNO055 operation modes ---
OPERATION_MODE_CONFIG = 0x00
OPERATION_MODE_NDOF   = 0x0C

ref_alt_ft_home =1123 	# ref_num = 1
ref_loc_hone = "Camas" 	# ref_num = 1
ref_alt_ft_msl = 0		# ref_num = 2
ref_loc_beach = "Beach" # ref_num = 2
ref_num = 1
ref_loc = ref_loc_hone
ref_alt_ft = ref_alt_ft_home

MPS_TO_MPH = 2.23694
sequence_num = 0
SEA_LEVEL_PRESSURE = 1013.25  # Standard sea-level pressure in hPa
altitude_offset = 0  # Offset for zeroing altitude
pause_time = 0.01
mark_count = 0
cal_count = 0
SDcard_eject_halt = 0
display_counter = 0
dps310_cal_time = 0
mark_now = 0
previous_airflow = 0
air_error_cnt = 0
air_error = 0

magnetic_deviation = 13.00

max_feet = 0
min_feet = 0
Hi_time_str = " "
Lo_time_str = " "

max_airflow = 0			# Set max air flow to 0
min_airflow = 33.6 			# 16.2 mph is max for FS3000-1005 sensor
Hi_airflow_time_str = " " 	# Set default time strings
Lo_airflow_time_str = " "	# Set default time strings

# Built-in LED setup
led_status = True
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led_blink_time = 50 # milliseconds


# -- Altitude header status
first_call_altitude = True  # Used to print header only once


# -- Position header status
first_call_position = True  # Used to print header only once


# -- Summaryu header status
first_call_summary = True  # Used to print header only once

# --- Wind buffers must be declared globally or passed in ---
short_term = []
medium_term = []
long_term = []     

dv_dt_buffer = []
jerk_buffer = []

# --- Wind State variables preserved across calls ---
prev_wind = None
prev_dv_dt = None
first_call_wind = True  # Used to print header only once



# ----------------------------------------------------
# Create Objects
# ----------------------------------------------------

# Built-in NeoPixel setup
# nexopixel_status = True
# pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # One NeoPixel
# pixel.brightness = 0.5  # Adjust brightness (0.0 to 1.0)
neopixel_blink_time = 1

# Initialize a NeoPixel; many CircuitPython boards (like the Adafruit Feather or Circuit Playground Express)
# have a built-in NeoPixel accessible via board.NEOPIXEL.
# Replace board.NEOPIXEL and the pixel count as required.
num_pixels = 1
pixels = neopixel.NeoPixel(board.NEOPIXEL, num_pixels, brightness=0.5, auto_write=True)

"""

# Connect to the SD card and mount the filesystem.
cs = digitalio.DigitalInOut(board.SD_CS)
sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)

sd_mounted = False  # Assume failure initially

try:
    sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    sd_mounted = True
    #print("SD card mounted successfully.")
except OSError as e:
    #  ESC [ 2 J   → clear screen
    #  ESC [ H     → move cursor to home (optional)
    #  \x1b[{1};1H" → move cursor to top left
    print("\x1b[2J",end="")  # VT100 escapes codes

    print("SD missing")
    print("OSError:", e)

"""

# Set up the ADC on A2 (Battery Voltage Monitor)
vbat_adc = analogio.AnalogIn(board.A0)

# i2c = board.I2C()  # uses board.SCL and board.SDA
i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
rtc = adafruit_ds3231.DS3231(i2c)

displayio.release_displays()
display_bus = I2CDisplayBus(i2c, device_address=0x3D)

###SH1107
# Width, height and rotation for Monochrome 1.12" 128x128 OLED
WIDTH = 128
HEIGHT = 128
ROTATION = 180

# Border width
BORDER = 2

display = SH1107(
    display_bus,
    width=WIDTH,
    height=HEIGHT,
    display_offset=DISPLAY_OFFSET_ADAFRUIT_128x128_OLED_5297,
    rotation=ROTATION,
)
###

# Initialize I2C and sensor
#i2c = busio.I2C(board.SCL, board.SDA)
dps = adafruit_dps310.DPS310(i2c)

bno = BNO055_I2C(i2c, address=0x29)

# Renesas FS3000-1015 air velocity sensor
#i2c = board.I2C()  # uses board.SCL and board.SDA
sensor_fs3000 = FS3000_1015(i2c)

# Set high oversampling for better accuracy
dps.pressure_oversample = 128  # Can be 1, 2, 4, 8, 16, 32, 64, or 128
dps.temperature_oversample = 2  # Improves temperature compensation

# Configure D4 as an input with an internal pull-up resistor.
pin = digitalio.DigitalInOut(board.D4)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP  # Ensures the pin reads high when not connected to ground.

# Connect to the SD card and mount the filesystem.
cs = digitalio.DigitalInOut(board.SD_CS)
sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)

sd_mounted = False  # Assume failure initially

try:
    sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    sd_mounted = True
    #print("SD card mounted successfully.")
except OSError as e:
    #  ESC [ 2 J   → clear screen
    #  ESC [ H     → move cursor to home (optional)
    #  \x1b[{1};1H" → move cursor to top left
    print("\x1b[2J",end="")  # VT100 escapes codes

    print("SD missing")
    print("OSError:", e)


#
# Set date & time if needed
#
if False:  # change to True if you want to set the time! False
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    #
    # t = time.struct_time((2025, 3, 24, 11, 11, 0, 0, 83, 0))
    #
    # 2025: Year
    # 3: Month (March)
    # 24: Day of the month
    # 11: Hour (in 24-hour format)
    # 11: Minute
    # 0: Second
    # 0: Weekday (with 0 typically representing Monday in Python’s time module)
    # 83: Day of the year (March 24 is the 83rd day in a non-leap year)
    # 0: Daylight Saving Time flag (0 indicates DST is not in effect)
    #
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    
    t = time.struct_time((2025, 6, 26, 14, 39, 0, 3, 177, 0))

    if DEBUG:
        print("Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t

#
# Moving average object
#

class MovingAverage:
    def __init__(self, window_size=60):
        self.window_size = window_size
        self.buffer = [0] * window_size  # Fixed-size list to store sensor values
        self.index = 0                  # Points to the next insertion index in the circular buffer
        self.count = 0                  # Number of samples collected so far (maxes at window_size)
        self.total = 0.0                # Running sum of the values in the buffer

    def update(self, value):
        """
        Adds a new sensor value, updates the moving average, and returns the current average.
        """
        # If the buffer is not fully populated, simply add the new value.
        if self.count < self.window_size:
            self.total += value
            self.buffer[self.index] = value
            self.count += 1
        else:
            # The buffer is full: subtract the oldest value and add the new value.
            self.total = self.total - self.buffer[self.index] + value
            self.buffer[self.index] = value

        # Move the index in a circular manner.
        self.index = (self.index + 1) % self.window_size

        return self.total / self.count  # Return the average of the values stored

# Create an instance of the battery voltage filter with a window size of 16.
avg_bat_filter = MovingAverage(60)

# Create an instance of the wind flow filter with a window size of 60. One minute of air flow data.
avg_air_flow_filter = MovingAverage(60)



# ----------------------------------------------------
# Functions for SD writes to .csv file
# ----------------------------------------------------



def log_to_sd(seq, tto, mark2, timest, p0, p1, p2, p3, p4, p4a, p5, p6, p7, p8, afmps, afmph, afave, afmax, afmin, aerr):
    global first_call_altitude
    # open file for append
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/" + VERSION_string + "_" + date_now + "_altitude" + ".csv"

    # Print header once
    if first_call_altitude:
        header = "#, TTO, Mark,   Time,   Alt Ft, hPa, Dif Ft,  H Ft, L Ft, inHg, Temp, Tcpu, Vbat, VbatAv, Wind mps, Wind mph, Wind Ave, Wind Max, AflowMin, Wind Error\n"
        first_call_altitude = False
        try:
            with open(file_name, "ab") as df:
                df.write(header)
        except OSError:
            print("SD data write error")

    try:
        with open(file_name, "a") as f:
             f.write(
                 "%d, %s, %d, %s,  %0.1f, %0.3f, %0.1f, %0.1f, %0.1f, %0.5f, %0.2f, %0.2f, %0.2f, %0.2f, %0.4f, %0.4f, %0.4f, %0.4f, %0.4f, %d\n" %
                 (seq, tto, mark2, timest, p0, p1, p2, p3, p4, p4a, p5, p6, p7, p8, afmps, afmph, afave, afmax, afmin, aerr)
             )
    except OSError:
        print("Error opening SD altitude log file.")


def log_summary_sd(time_str, altitude):
    """Continuously read and log all BNO055 outputs (including compass heading) to CSV."""
    global display_counter
    global mark_now
    global first_call_summary
    global avg10, gust10

    # CSV column descriptions:
    # timestamp        -- seconds since power-on (time.monotonic()), two-decimal precision.
    # a                -- altitude calibration status (feet).
    # z_kite (heading) -- Compass heading (0-360°).
    # y_kite (pitch)   -- Pitch (-90° down,  +90° up).
    # x_kite (roll)    -- Roll (-180° CCW, +180° CW faceing x axis).
    # temp_f             -- BNO055 temperature (°F).

    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/" + VERSION_string + "_" + date_now + "_summary" + ".csv"

    tt        = time_str
    m         = mark
    a         = altitude
    am        = max_feet
    x, y, z   = bno.euler or (None, None, None) # Euler data is buggy, fix is below
    y_kite    = y                  # Pitch
    temp1      = z
    z_kite    = (x + 90.0) % 360.0 # Compus heading
    true_heading = (z_kite + magnetic_deviation) % 360.0
    x_kite    = temp1              # Roll
    temp_c    = bno.temperature
    temp_f    = temp_c * 9 / 5 + 32
#    airflow_mps
#    airflow_mph
#    air_flow_moving_avg
#    max_airflow
#    min_airflow
# 	 air_error
        
    # Print header once
    if first_call_summary:
        header = (
            "#, Time, Mark, Alt, Max Alt, TrueH, MagH, Pitch, Roll, Temp, Wind, WMax, WErr \n"
        )
        first_call_summary = False
        try:
            with open(file_name, "ab") as df:
                df.write(header)
        except OSError:
            print("SD data write error")

    row = (
        f"{sequence_num:d}, {tt}, {m}, "
        + f"{a:.1f}, {am:.1f}, {true_heading:.1f}, {z_kite:.1f}, {y_kite:.1f}, {x_kite:.1f}, "
        + f"{temp_f:.1f}, {airflow_mph:.1f}, {max_airflow:.1f}, {air_error:d} \n"
    )

    try:
        with open(file_name, "ab") as df:
            df.write(row.encode())
    except OSError:
        print("Error opening SD summary log file.")

    tsc = time.monotonic() - dps310_cal_time
    hours = tsc // 3600
    remaining_seconds = tsc % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
#    hms_string = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    tsc_str = "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

    battery_v = get_battery_voltage()

    if SUMMARY_PRINT:
        if display_counter%2 == 0 :
            # --- Erase entire display (VT100) ---
            #  ESC [ 2 J   → clear screen
            #  ESC [ H     → move cursor to home (optional)
            #  \x1b[{1};1H" → move cursor to top left
            print("\x1b[2J",end="")  # VT100 escapes codes
            # Move cursor to top-left (row 1, col 1)
            print(f"\x1b[{1};1H", end="") # VT100 escapes codes
            print(tt, "  ",tsc_str)
            print(f"{a:.1f}'",f" Max {max_feet:.1f}'")
            print(f"TH {true_heading:.1f}°, MH {z_kite:.1f}°")
            print(f"Pit: {y_kite:.0f}°",f" Rol: {x_kite:.0f}°")
            print(f"{avg10:.1f} mph  G {gust10:.1f} mph")
            print(f"Temp: {temp_f:.1f}° F")
            #print("Air error:", air_error)
            if mark_now:
                print(f"Bat: {battery_v:.2f} V **MARK {m:.0f}")
                mark_now =0
            else:
                print(f"Bat: {battery_v:.2f} V")
                
    display_counter += 1


def log_bno055_data_sd(time_str):
    global first_call_position

    # CSV column descriptions updated to include compass_heading:
    # timestamp        -- seconds since power-on (time.monotonic()), two-decimal precision.
    # sys              -- system calibration status (0–3).
    # gyro             -- gyro calibration status (0–3).
    # accel            -- accel calibration status (0–3).
    # mag              -- mag calibration status (0–3).
    # euler_x          -- roll (°).
    # euler_y          -- pitch (°).
    # euler_z          -- yaw from fusion (°).
    # heading          -- alias for euler_z (°).
    # compass_heading  -- normalized 0–360° compass bearing.
    # quat_w, quat_x/y/z -- quaternion components.
    # lin_acc_x/y/z    -- linear acceleration (m/s²).
    # grav_x/y/z       -- gravity vector (m/s²).
    # raw_mag_x/y/z    -- raw mag readings (µT).
    # temp             -- temperature (°C).

    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/" + VERSION_string + "_" + date_now + "_position" + ".csv"

    # Print header once
    if first_call_position:
        header = (
            "#, times, sys, gyro, accel, mag, e_x, e_y, e_z, heading, compass, "
            "q_w, q_x, q_y, q_z, lin_acc_x, lin_acc_y, lin_acc_z, "
            "grav_x, grav_y, grav_z, r_mag_x, r_mag_y, r_mag_z, temp \n"
        )
        first_call_position = False
        try:
            with open(file_name, "ab") as df:
                df.write(header)
        except OSError:
            print("SD data write error")

    tt        = time_str
    sys_s, gyr_s, acc_s, mag_s = bno.calibration_status
    e        = bno.euler or (0.0, 0.0, 0.0)
    heading  = e[2]
    # normalize to [0,360)
    compass = (heading + 360.0) % 360.0
    q        = bno.quaternion or (0.0, 0.0, 0.0, 0.0)
    la       = bno.linear_acceleration or (0.0, 0.0, 0.0)
    g        = bno.gravity or (0.0, 0.0, 0.0)
    raw_mag  = bno.magnetic or (0.0, 0.0, 0.0)
    temp     = bno.temperature

    row = (
        f"{sequence_num:d}, {tt}, "
        + f"{sys_s}, {gyr_s}, {acc_s}, {mag_s}, "
        + f"{e[0]:.3f}, {e[1]:.3f}, {e[2]:.3f}, {heading:.21f}, {compass:.1f}, "
        + f"{q[0]:.5f}, {q[1]:.5f}, {q[2]:.5f}, {q[3]:.5f}, "
        + f"{la[0]:.5f}, {la[1]:.5f}, {la[2]:.5f}, "
        + f"{g[0]:.5f}, {g[1]:.5f}, {g[2]:.5f}, "
        + f"{raw_mag[0]:.5f}, {raw_mag[1]:.5f}, {raw_mag[2]:.5f}, "
        + f"{temp:.1f}\n"
    )

    try:
        with open(file_name, "ab") as df:
            df.write(row.encode())
    except OSError:
        print("Error opening SD position log file.")


def log_wind_data(air_flow_measurement):
    global prev_wind, prev_dv_dt, first_call_wind
    global avg10, gust10
    global avg2m, gust2m

    wind = air_flow_measurement

    # Append to buffers
    append_with_limit(short_term, wind, 10)
    append_with_limit(medium_term, wind, 120)
    append_with_limit(long_term, wind, 600)

    # Compute wind stats
    avg10, gust10, lull10, turb10 = compute_wind_stats(short_term)
    avg2m, gust2m, lull2m, turb2m = compute_wind_stats(medium_term)
    avg10m, gust10m, lull10m, turb10m = compute_wind_stats(long_term)

    # Compute rate of change and jerk
    if prev_wind is not None:
        dv_dt = wind - prev_wind
        append_with_limit(dv_dt_buffer, dv_dt, 10)

        if prev_dv_dt is not None:
            jerk = dv_dt - prev_dv_dt
            append_with_limit(jerk_buffer, jerk, 10)
        else:
            jerk = 0.0
    else:
        dv_dt = 0.0
        jerk = 0.0

    prev_wind = wind
    prev_dv_dt = dv_dt

    # Display formatted output
    t = time.monotonic()

    if WIND_PRINT:
        # --- Erase entire display (VT100) ---
        #  ESC [ 2 J   → clear screen
        #  ESC [ H     → move cursor to home (optional)
        print("\x1b[2J\x1b[H", end="")  # VT100 escapes codes

        print(Now_time_str, f"{air_flow_measurement:3.1f} {max_airflow:3.1f}")
        print(f"10A {avg10:3.1f} G {gust10:3.1f}")
        print(f"L {lull10:3.1f} T {turb10:3.1f} ")
        print(f"RC {dv_dt:+3.2f} J {jerk:+3.2f}")
        print(f"2MA {avg2m:3.1f} G {gust2m:3.1f}")
        print(f"L {lull2m:3.1f} T {turb2m:3.1f}")
        print(f"10MA {avg10m:3.1f} G {gust10m:3.1f}")
        print(f"L {lull10m:3.1f} T {turb10m:3.1f}")

    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/" + VERSION_string + "_" + date_now + "_wind" + ".csv"

    # Print header once
    if first_call_wind:
        header = "#, TTO, Time, Mark, Alt, Alt>GND, Wind, WindMax, WindErr, 10sAve, 10sGust,10sLull, 10sTurb, 10sRofC, 10sJerk, 2mAve, 2mG, 2mL, 2mT, 10mAve, 10mG, 10mL, 10mT\n"
        first_call_wind = False
        try:
            with open(file_name, "ab") as df:
                df.write(header)
        except OSError:
            print("SD data write error")

    row = (
        f"{sequence_num:d}, {tto:s}, {Now_time_str:s}, {mark:d}, {current_alt_ft:4.1f}, {altitude_above_gnd:4.1f}, "
        + f"{airflow_mph:3.1f}, {max_airflow:3.1f}, {air_error}, "
        + f"{avg10:3.1f}, {gust10:3.1f}, {lull10:3.1f}, "
        + f"{turb10:3.1f}, {dv_dt:+3.2f}, {jerk:+3.2f}, "
        + f"{avg2m:3.1f}, {gust2m:3.1f}, {lull2m:3.1f}, {turb2m:3.1f}, "
        + f"{avg10m:3.1f}, {gust10m:3.1f}, {lull10m:3.1f}, {turb10m:3.1f}\n"
    )

    try:
        with open(file_name, "ab") as df:
            df.write(row.encode())
    except OSError:
        print("Error opening SD wind log file.")


def pressure_average(measurements: int = 64) -> float:
    global dps310_cal_time
    """
    Reads a specified number of pressure measurements from the DPS310 sensor,
    calculates statistics on the measurements (average, minimum, maximum, range in hPa,
    altitude range in inches, and standard deviation), prints each statistic on a line 
    limited to ~21 characters with a 3-second delay between lines, pauses for 10 seconds,
    and returns the average pressure value.

    Parameters:
        measurements (int): The number of pressure measurements to take. Default is 64.

    Returns:
        float: The average pressure value in hPa.
    """
    NeoPixel_LED((0, 255, 0))

    # Get RTC date and time
    t = rtc.datetime
    Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    date_str = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)    
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/" + VERSION_string + "_" + date_now + "_cal" + ".txt"

    # Get RTC date and time
    t = rtc.datetime
    Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    date_str = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)

    if True:
        # --- Erase entire display (VT100) ---
        #  ESC [ 2 J   → clear screen
        #  ESC [ H     → move cursor to home (optional)
        print("\x1b[2J\x1b[H", end="")  # VT100 escapes codes
        print("Altitude Calibration")
        print("Base hPa cal", measurements,"rdg")
        print(ref_loc, ref_alt_ft, "ft")
    readings = []
    try:
        with open(file_name, "a") as f:
            f.write("*\n")
            f.write("* " + date_str + " " + Now_time_str + "\n")
            f.write("* Hardware . Software version: " + VERSION_string + "\n")
            f.write("* Altitude referance calibration\n")    
        for i in range(measurements):
            if True:
                print("\x1b[2K", "\r", i, end="")
            # Read the pressure measurement from the DPS310 sensor
            pressure_value = dps.pressure
            
            with open(file_name, "a") as f:
                f.write("* Measure %d %6.4f\n" % (i, pressure_value))

            readings.append(pressure_value)
            # Small delay between measurements for sensor stability
            time.sleep(0.1) # Delay for DPS310
    except OSError:
        print("SD data write error")

    if True:
        print(" ")
    # Calculate pressure statistics
    avg_pressure = sum(readings) / measurements
    min_pressure = min(readings)
    max_pressure = max(readings)
    pressure_range = max_pressure - min_pressure  # in hPa
    
    # Calculate the variance and standard deviation
    variance = sum((x - avg_pressure) ** 2 for x in readings) / measurements
    std_dev = math.sqrt(variance)
    
    # Calculate altitude for the extreme pressure values using hpa_to_feet.
    altitude_at_min_pressure = hpa_to_feet(min_pressure)  # higher altitude (ft)
    altitude_at_max_pressure = hpa_to_feet(max_pressure)  # lower altitude (ft)
    altitude_range_feet = altitude_at_min_pressure - altitude_at_max_pressure
    altitude_range_inches = altitude_range_feet * 12
    try:
        with open(file_name, "a") as f:
            f.write("*\n")
            f.write("* Pressure Calibration Summary\n")
            f.write("* Number of measurements %d\n" % (measurements))
            f.write("* Average hPa %6.3f\n" % (avg_pressure))
            f.write("* Minimum hPa %6.3f\n" % (min_pressure))
            f.write("* Maximum hPa %6.3f\n" % (max_pressure))
            f.write("* Standand deviation hPa %6.3f\n" % (std_dev))
            f.write("* Range in hPa %6.3f\n" % (pressure_range))
            f.write("* Range in inches %6.3f\n" % (altitude_range_inches))
            f.write("* Referance Location " + ref_loc + "\n")        
            f.write("* Referance Altitude in feet %7.1f\n" % (ref_alt_ft))
    except OSError:
        print("SD data write error")

    NeoPixel_LED((0, 0, 0))
    dps310_cal_time = time.monotonic()
    print("Average %6.3f hPa" % (avg_pressure))
    print("Std dev %6.3f hPa" % (std_dev))
    print("Ref Alt %7.1f'" % (ref_alt_ft))
    time.sleep(9.0)
    return avg_pressure


# ----------------------------------------------------
# Functions for SD writes txt
# ----------------------------------------------------


def monitor_bno055_calibration(timeout=180):
    """
    Monitor calibration with LED feedback and log to microSD.
    """
       
    pixel_blink()
    
    # Get RTC date   
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/" + VERSION_string + "_" + date_now + "_cal" + ".txt"

    # Get RTC time
    t = rtc.datetime
    Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)


    header = f"\n=== Calibration Start: Now_time_str ===\n"
    header = Now_time_str + " " + header
    try:
        with open(file_name, "ab") as log_file:
            log_file.write(header.encode())
    except OSError:
        if BNO_CAL_PRINT :
            print("Error opening SD calibration log file.")
            print("Starting calibration...")

    bno.mode = OPERATION_MODE_CONFIG
    time.sleep(0.1)
    bno.mode = OPERATION_MODE_NDOF
    time.sleep(0.1)

    start = time.monotonic()
    warned = False
    while True:
        
        # Get RTC time
        t = rtc.datetime
        Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)

        sys_s, gyr_s, acc_s, mag_s = bno.calibration_status
        status = f"Status: Sys={sys_s}/3, Gyr={gyr_s}/3, Acc={acc_s}/3, Mag={mag_s}/3"
        status = Now_time_str+" "+status

        if BNO_CAL_PRINT :
            # Move cursor to top-left (row 1, col 1)
            print(f"\x1b[{1};1H", end="")   # VT100 escapes codes
            print("BNO055 Cal Status:")
            print("Sys 3 =", sys_s)
            print("Acc 3 =", acc_s, "45 stop")
            print("Mag 3 =", mag_s, "Fig 8")            
            print("Gyr 3 =", gyr_s, "Fixed")

        try:
            with open(file_name, "ab") as log_file: 
                log_file.write(f"{status}\n".encode())
        except OSError:
            pass

        if acc_s < 3:
            pixels.fill((255, 0, 0)); phase = f"Accel {acc_s}/3 Red LED \n"
        elif mag_s < 3:
            pixels.fill((0, 255, 0)); phase = f"Mag {mag_s}/3 Green LED \n"
        elif gyr_s < 3:
            pixels.fill((0, 0, 255)); phase = f"Gyro {gyr_s}/3 Blue LED \n"
        elif sys_s < 3:
            pixels.fill((255, 255, 0)); phase = f"Sys {sys_s}/3 Yellow LED\n"
        else:
            pixels.fill((0, 255, 255)); phase = "Done Cyan LED           "
        if BNO_CAL_PRINT :
            print(phase)
        try:
            with open(file_name, "ab") as log_file:
                log_file.write(f"{phase}\n".encode())
        except OSError:
            pass

        if not warned and sys_s < 3 and (time.monotonic() - start) > timeout:
            hint = "Hint: rotate around all axes."
            if BNO_CAL_PRINT :
                print(hint)
            try:
                with open(file_name, "ab") as log_file:
                    log_file.write(f"{hint}\n".encode())
            except OSError:
                pass
            warned = True

        if (sys_s, gyr_s, acc_s, mag_s) == (3, 3, 3, 3):
            break
        time.sleep(1.0)

    try:
        offs_a = bno.offsets_accelerometer
        offs_m = bno.offsets_magnetometer
        offs_g = bno.offsets_gyroscope
        out = f"Offsets\nA{offs_a}\nM{offs_m}\nG{offs_g}\n"

        # Get RTC time
        t = rtc.datetime
        Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)

        out = Now_time_str +" "+ out
        if BNO_CAL_PRINT :
            # Move cursor to top-left (row 1, col 1)
            print(f"\x1b[{1};1H", end="")   # VT100 escapes codes
            print("BNO055 Cal Done")
            print(f"A{offs_a}")    
            print(f"M{offs_m}")
            print(f"G{offs_g}")
            pixel_blink(5)
        with open(file_name, "ab") as log_file:
            log_file.write(out.encode())
    except Exception as e:
        if BNO_CAL_PRINT :
            print("SD offsets read error", e)

    bno.mode = OPERATION_MODE_NDOF


def log_to_sd_version(verson):
    # Log system info to SD card.

# Get RTC date and time
    t = rtc.datetime
    Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    date_str = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/" + VERSION_string + "_" + date_now + "_cal" + ".txt"

    date_time_str = date_str + " " + Now_time_str

    try:
        with open(file_name, "a") as f:
            f.write(" \n")
            f.write("***********************************************************************\n")
            f.write("* "+date_time_str+"\n")
            f.write("* Hardware . Software version: "+VERSION_string+"\n")
            f.write("* \n")
            
            # Log memory status.
            gc.collect()  # Run garbage collection to get an accurate reading
            free_mem = gc.mem_free()  # Get free memory
            allocated_mem = gc.mem_alloc()  # Get allocated memory
            total_mem = free_mem + allocated_mem  # Total memory available
            mem_used = allocated_mem
            mem_free = free_mem
            mem_total = total_mem
            mem_Kb_used =  mem_used/1000
            mem_Kb_free =  mem_free/1000  
            mem_Kb_total =  mem_total/1000      
            mem_used_percent = (mem_used / mem_total) * 100
            mem_free_percent = (mem_free / mem_total) * 100
            f.write("* CircuitPython Memory Status\n")
            f.write(f"* Used {mem_Kb_used:.1f} Kb {mem_used_percent:.1f}%\n")
            f.write(f"* Free {mem_Kb_free:.1f} Kb {mem_free_percent:.1f} %\n")
            f.write(f"* Total {mem_Kb_total:.1f} Kb\n\n")

            # Log CPU information including clock speed, unique ID, and CircuitPython version.
            cpu_freq = microcontroller.cpu.frequency  # Get CPU frequency in Hz
            cpu_temp = microcontroller.cpu.temperature  # Get CPU temperature in Celsius
            unique_id = microcontroller.cpu.uid  # Get the unique ID of the chip
            python_version = sys.version  # Get CircuitPython version
            board_name = os.uname().machine  # Get board name
            os_version = os.uname().version  # Get CircuitPython OS version
            # Format the unique ID separately before printing
            unique_id_str = " ".join(["{:02X}".format(x) for x in unique_id])
            f.write("* Altimeter Info\n") 
            f.write(f"* {board_name}\n")  
            f.write(f"* CPU Freq: {cpu_freq / 1_000_000:.2f} MHz\n")
            f.write(f"* CPU Temp: {cpu_temp:.1f}°C {(cpu_temp * 9/5) + 32:.1f}°F\n")
            f.write(f"* ID: {unique_id_str}\n")
            f.write(f"* CPy V: {python_version}\n")
            f.write(f"* OS V: {os_version}\n")
    except OSError:
        print("SD data write error")


def sd_free_bytes() -> int:
    """
    Return the number of bytes still free on the SD card
    mounted at '/sd' on an Adafruit RP2040 Adalogger.
    If the SD card is not mounted, return -1 and print an error.
    """
    try:
        stat = os.statvfs('/sd')
        free_blocks = stat[3]  # bfree
        block_size = stat[1]   # bsize
        free_bytes = free_blocks * block_size
        return free_bytes
    except OSError as e:
        #  ESC [ 2 J   → clear screen
        #  ESC [ H     → move cursor to home (optional)
        #  \x1b[{1};1H" → move cursor to top left
        print("\x1b[2J",end="")  # VT100 escapes codes

        print("SD missing")
        print("OSError:", e)
        while True:
            pass
        return -1



# ----------------------------------------------------
# Functions
# ----------------------------------------------------


# Helper function to append to a buffer with max length
def append_with_limit(buffer, value, maxlen):
    buffer.append(value)
    if len(buffer) > maxlen:
        buffer.pop(0)


# --- Helper function for wind statistics ---
def compute_wind_stats(buffer):
    if len(buffer) == 0:
        return (0.0, 0.0, 0.0, 0.0)
    avg = sum(buffer) / len(buffer)
    gust = max(buffer)
    lull = min(buffer)
    turb = gust - lull
    return (avg, gust, lull, turb)


def pixel_blink(blinks=1, duration=1, red=255, green=255, blue=255):
    for index in range(blinks):
        pixels.fill((red, green, blue))
        time.sleep(duration)
        pixels.fill((0, 0, 0))
        time.sleep(duration)


def print_numbers():
    """
    Print all displayable ASCII characters (from space through tilde)
    as a single, contiguous string.
    """
    # ASCII codes 32 (space) through 126 (~) are the printable characters
    displayable = ''.join(chr(code) for code in range(48, 58))
    displayable = displayable + displayable
    print(displayable)


def print_displayable_ascii():
    """
    Print all displayable ASCII characters (from space through tilde)
    as a single, contiguous string.
    """
    #  !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
    # ASCII codes 32 (space) through 126 (~) are the printable characters
    displayable = ''.join(chr(code) for code in range(32, 127))
    print(displayable)


# wrap into conventional ranges
def wrap180(a): return (a + 180) % 360 - 180


def quaternion_to_euler(quat):
    """
    Convert a BNO055 quaternion (w, x, y, z) to aerospace Euler angles:
      roll  = rotation about X (–180°…+180°)
      pitch = rotation about Y (–90°…+90°)
      yaw   = rotation about Z (–180°…+180°)
    """
    w, x, y, z = quat

    # roll (X-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.degrees(math.atan2(sinr_cosp, cosr_cosp))

    # pitch (Y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        # use 90° if out of range
        pitch = math.degrees(math.copysign(math.pi / 2, sinp))
    else:
        pitch = math.degrees(math.asin(sinp))

    # yaw (Z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.degrees(math.atan2(siny_cosp, cosy_cosp))

    return roll, pitch, yaw


def bno_map_axis():
# --- Optional: Axis Remapping ---
# Use sensor.axis_remap to align sensor axes to your board orientation.
# The tuple format is: (X_axis, Y_axis, Z_axis, X_sign, Y_sign, Z_sign)
# - X_axis, Y_axis, Z_axis: one of AXIS_REMAP_X/Y/Z to map board axes to sensor axes.
# - X_sign, Y_sign, Z_sign: one of AXIS_REMAP_POSITIVE/NEGATIVE to flip axis direction.
# Example: swap X and Y axes and invert Y direction:
    bno.mode = CONFIG_MODE
    time.sleep(0.1)
    bno.axis_remap = (
        AXIS_REMAP_X,        # board X ← sensor X
        AXIS_REMAP_Z,        # board Y ← sensor Z
        AXIS_REMAP_Y,        # board Z ← sensor Y
        AXIS_REMAP_POSITIVE, # keep X-sign
        AXIS_REMAP_POSITIVE, # keep Y-sign
        AXIS_REMAP_POSITIVE  # keep Z-sign (flip to NEGATIVE if gravity reads –9.8 here)
    )
    bno.mode = NDOF_MODE
    time.sleep(0.1)


def bno_mapping():
    """
    Remap raw Euler axes to board coordinates by swapping X and Y:
      x (roll)  = sensor pitch (raw_y),
      y (pitch) = sensor roll  (raw_x),
      z (yaw)   = sensor yaw   (raw_z).
    Returns a tuple (x, y, z) in degrees.
    """
    raw_x, raw_y, raw_z = bno.euler or (None, None, None)
    # Swap sensor X and Y axes to match board orientation
    x = raw_y   # board X uses sensor Y (pitch)
    y = raw_x   # board Y uses sensor X (roll)
    z = raw_z   # board Z uses sensor Z (yaw)
    return x, y, z

    
def set_bno055_calibration_values():
    """
    1. Print the current calibration offsets stored in the BNO055.
    2. Apply new predefined offsets.
    3. Print the updated offsets to confirm.

    Predefined Offsets:
      Accelerometer A = (14, –13, –14)
      Magnetometer M = (272, –427, –475)
      Gyroscope G = (–1, 1, –1)
    """
    # 1) Print current offsets
    try:
        current_a = bno.offsets_accelerometer
        current_m = bno.offsets_magnetometer
        current_g = bno.offsets_gyroscope
        print(f"Current Offsets -> Accel: {current_a}, Mag: {current_m}, Gyro: {current_g}")
    except AttributeError as e:
        print("Error reading current offsets:", e)

    # 2) Load new offsets with detailed meaning
    new_a = (14, -13, -14)
    # new_a[0]: Accelerometer X-axis offset in LSB (compensates X-axis bias)
    # new_a[1]: Accelerometer Y-axis offset in LSB (compensates Y-axis bias)
    # new_a[2]: Accelerometer Z-axis offset in LSB (compensates Z-axis bias)

    new_m = (272, -427, -475)
    # new_m[0]: Magnetometer X-axis hard-iron offset in LSB (corrects X-axis magnetic bias)
    # new_m[1]: Magnetometer Y-axis offset in LSB (corrects Y-axis magnetic bias)
    # new_m[2]: Magnetometer Z-axis offset in LSB (corrects Z-axis magnetic bias)

    new_g = (-1, 1, -1)
    # new_g[0]: Gyroscope X-axis offset in LSB (adjusts X-axis angular bias)
    # new_g[1]: Gyroscope Y-axis offset in LSB (adjusts Y-axis angular bias)
    # new_g[2]: Gyroscope Z-axis offset in LSB (adjusts Z-axis angular bias)

    try:
        bno.offsets_accelerometer = new_a
        bno.offsets_magnetometer  = new_m
        bno.offsets_gyroscope     = new_g
        print("Loaded new calibration offsets.")
    except AttributeError as e:
        print("Error setting new offsets:", e)

    # 3) Print updated offsets to verify
    try:
        updated_a = bno.offsets_accelerometer
        updated_m = bno.offsets_magnetometer
        updated_g = bno.offsets_gyroscope
        print(f"Updated Offsets -> Accel: {updated_a}, Mag: {updated_m}, Gyro: {updated_g}")
    except AttributeError as e:
        print("Error reading updated offsets:", e)


# --- Utility functions to print individual BNO055 readings ---
def bno_sys():
    """Print system calibration status (0–3)."""
    sys_s = bno.calibration_status[0]
    print(f"System calibration status: {sys_s}/3")


def bno_gyro():
    """Print gyroscope calibration status (0–3)."""
    gyro_s = bno.calibration_status[1]
    print(f"Gyro calibration status: {gyro_s}/3")


def bno_accel():
    """Print accelerometer calibration status (0–3)."""
    accel_s = bno.calibration_status[2]
    print(f"Accel calibration status: {accel_s}/3")


def bno_mag():
    """Print magnetometer calibration status (0–3)."""
    mag_s = bno.calibration_status[3]
    print(f"Mag calibration status: {mag_s}/3")


def bno_euler_kite():
    """
    Print fused Euler angles with axis notation and valid ranges:
      x (roll):  in degrees, range [-180° CCW, +180° CW faceing x axis] Bug x is yaw 0 to 360 degrees
      y (pitch): in degrees, range [-90° down,  +90° up]  
      z (yaw):   in degrees, range [-180°, +180°] Bug z is roll [-180° CCW, +180° CW faceing x axis]
    """
    x, y, z = bno.euler or (None, None, None)

    y_kite = y
    temp = z
    z_kite = (x + 90.0) % 360.0
    x_kite = temp
    
#    print(f"Euler angles -> Roll (-180° CCW to +180° CW): {x_kite}°, Pitch (90° down to +90° up): {y_kite}°, Yaw (0° to +360°): {z_kite}°")
    return x_kite, y_kite, z_kite


def bno_euler_kite_print():
    """
    Print fused Euler angles with axis notation and valid ranges:
      x (roll):  in degrees, range [-180° CCW, +180° CW faceing x axis] Bug x is yaw 0 to 360 degrees
      y (pitch): in degrees, range [-90° down,  +90° up]  
      z (yaw):   in degrees, range [-180°, +180°] Bug z is roll [-180° CCW, +180° CW faceing x axis]
    """
    x, y, z = bno.euler or (None, None, None)

    y_kite = y
    temp = z
    z_kite = (x + 90.0) % 360.0
    x_kite = temp


def bno_euler():
    """
    Bugs, could not fix with axis mapping.
    See above bno_euler_kite for fix. 
    Print fused Euler angles with axis notation and valid ranges:
      x (roll):  in degrees, range [-180°, +180°] Bug x is yaw 0 to 360 degrees -90° off
      y (pitch): in degrees, range [-90° down,  +90° up]  
      z (yaw):   in degrees, range [-180°, +180°] Bug z is roll [-180° CCW, +180° CW]
    """
    x, y, z = bno.euler or (None, None, None)
    print(f"Euler angles -> Roll (x -180° to +180°): {x}°, Pitch (y -90° to +90°): {y}°, Yaw (z -180° to +180°): {z}°")


def bno_heading():
    """Print yaw (Euler Z) as signed heading (–180 to +180°)."""
    heading = (bno.euler or (None, None, None))[2] #None (a falsey value) if the sensor hasn’t yet returned valid data
    print(f"Heading (Euler Z): {heading}°")


def bno_compass_heading():
    """Print normalized compass heading (0–360°)."""
    raw = (bno.euler or (0.0, 0.0, 0.0))[2]
    compass = (raw + 360.0) % 360.0
    print(f"Compass heading: {compass}°")


def bno_quat():
    """Print fused orientation quaternion (w, x, y, z)."""
    q = bno.quaternion or (None, None, None, None)
    print(f"Quaternion -> w: {q[0]}, x: {q[1]}, y: {q[2]}, z: {q[3]}")


def bno_lin_acc():
    """Print linear acceleration (m/s²) with gravity removed."""
    la = bno.linear_acceleration or (None, None, None)
    print(f"Linear accel -> X: {la[0]}, Y: {la[1]}, Z: {la[2]} (m/s²)")


def bno_grav():
    """Print gravity vector components (m/s²)."""
    g = bno.gravity or (None, None, None)
    print(f"Gravity vector -> X: {g[0]}, Y: {g[1]}, Z: {g[2]} (m/s²)")


def bno_raw_mag():
    """Print raw magnetometer readings (µT)."""
    r = bno.magnetic or (None, None, None)
    print(f"Raw magnetometer -> X: {r[0]}, Y: {r[1]}, Z: {r[2]} (µT)")


def bno_temp():
    """Print on-chip temperature in Celsius."""
    temp = bno.temperature
    print(f"Temperature: {temp}°C")


def dps310_to_noaa_inhg(local_pressure_hpa, altitude_ft, temperature_c):
    # Convert altitude to meters
    altitude_m = altitude_ft * 0.3048

    # Convert temperature to Kelvin
    temperature_k = temperature_c + 273.15

    # Constants
    gravity = 9.80665          # m/s²
    gas_constant_air = 287.05  # J/(kg·K)

    # Calculate sea-level pressure using the barometric formula with measured temperature
    exponent = (gravity * altitude_m) / (gas_constant_air * temperature_k)
    sea_level_pressure_hpa = local_pressure_hpa * math.exp(exponent)

    # Convert hPa to NOAA standard inHg
    sea_level_pressure_inhg = sea_level_pressure_hpa / 33.8639

    return sea_level_pressure_inhg


def get_battery_voltage():
    """Reads the battery voltage from A0 and converts it to real voltage."""
    # ADC reference voltage (RP2040 uses a 3.3V reference)
    ADC_REF_VOLTAGE = 3.3
    # RP2040 ADC resolution is 16-bit, but only 12 bits are used (0-65535 range)
    ADC_RESOLUTION = 65535
    # Voltage divider ratio (from Feather RP2040's built-in circuit)
    VOLTAGE_DIVIDER_RATIO = 2.0  # The circuit divides by 2, so we multiply back
    CAL = 1.0975
    raw_value = vbat_adc.value  # Read ADC value (0-65535)
    measured_voltage = (raw_value / ADC_RESOLUTION) * ADC_REF_VOLTAGE
    battery_voltage = measured_voltage * VOLTAGE_DIVIDER_RATIO * CAL  # Compensate for voltage divider
    return battery_voltage


def check_relay_status():
    # When the relay closes, D4 is connected to ground and reads low (False).
    # Return True if the pin reads 0.
    return False # not pin.value


def cpu_temperature_f():
    """
    Returns the current RP2040 internal temperature in Fahrenheit.
    """
    # Read temperature in Celsius from the internal sensor
    temp_c = microcontroller.cpu.temperature
    # Convert Celsius to Fahrenheit
    temp_f = temp_c * 9 / 5 + 32
    return temp_f


def DSP310_temperature_f():
    """
    Reads the temperature from the DPS310 sensor and returns it in degrees Fahrenheit.

    Returns:
        float: Temperature in Fahrenheit.
    """
    # The sensor returns temperature in Celsius.
    temp_c = dps.temperature
    # Convert Celsius to Fahrenheit.
    temp_f = (temp_c * 9 / 5) + 32
    return temp_f


def update_battery_voltage_color(battery_voltage):
    """
    Update a NeoPixel to display one of 8 colors based on the battery voltage.
    
    The voltage is assumed to be between:
      - 3.0V (lowest, displaying as black)
      - 4.2V (highest, displaying as white)
      
    The available colors (in order) are:
      0: Black   - (0, 0, 0)
      1: Blue    - (0, 0, 255)
      2: Cyan    - (0, 255, 255)
      3: Green   - (0, 255, 0)
      4: Yellow  - (255, 255, 0)
      5: Orange  - (255, 165, 0)
      6: Red     - (255, 0, 0)
      7: White   - (255, 255, 255)
    
    Parameters:
        battery_voltage (float): The current battery voltage.
    """
    # Define the battery voltage bounds for a typical single-cell LiPo.
    MIN_VOLTAGE = 3.0
    MAX_VOLTAGE = 4.2

    # Clamp the battery voltage into the accepted range
    battery_voltage = max(MIN_VOLTAGE, min(battery_voltage, MAX_VOLTAGE))
    
    # Map the battery voltage to a fraction between 0.0 and 1.0.
    fraction = (battery_voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)
    
    # Calculate the voltage level (0 to 7)
    levels = 8
    level = int(fraction * levels)
    if level >= levels:
        level = levels - 1

    # Define the eight color levels.
    colors = [
        (0,   0,   0),       # Level 0: Black
        (0,   0, 255),       # Level 1: Blue
        (0, 255, 255),       # Level 2: Cyan
        (0, 255,   0),       # Level 3: Green
        (255, 255, 0),       # Level 4: Yellow
        (255, 0, 255),       # Level 5: Magenta
        (255, 0,   0),       # Level 6: Red
        (255, 255, 255)      # Level 7: White
    ]
    
    # Get the color for the current level and update the NeoPixel.
    color = colors[level]
    pixels.fill(color)


def NeoPixel_LED(color=(255, 0, 0)): 
    # Red, green, blue
    # 0 is off, 255 is fully on
    pixels.fill(color)

def NeoPixel_Blink(millsec, color=(255, 0, 0)):
    """Blink the built-in NeoPixel for the given duration in milliseconds.
    
    Parameters:
        millsec (int): Duration of blink in milliseconds.
        color (tuple): RGB color for the NeoPixel.
    """
    if nexopixel_status: 
        pixels.fill((0, 0, 0))  # Ensure NeoPixel is off
        time.sleep(0.01)  # Small delay for visibility
        pixels.fill(color)  # Turn NeoPixel on with specified color
        time.sleep(millsec / 1000)  # Convert milliseconds to seconds
        pixels.fill((0, 0, 0))  # Turn NeoPixel off


def NeoPixel_Blink(millsec, color=(255, 0, 0)):
    """Blink the built-in NeoPixel for the given duration in milliseconds.
    
    Parameters:
        millsec (int): Duration of blink in milliseconds.
        color (tuple): RGB color for the NeoPixel.
    """
    if nexopixel_status: 
        pixels.fill((0, 0, 0))  # Ensure NeoPixel is off
        time.sleep(0.01)  # Small delay for visibility
        pixels.fill(color)  # Turn NeoPixel on with specified color
        time.sleep(millsec / 1000)  # Convert milliseconds to seconds
        pixels.fill((0, 0, 0))  # Turn NeoPixel off

def hpa_to_feet(pressure_hpa):
    """
    Convert atmospheric pressure (in hPa) to altitude (in feet)
    using the International Standard Atmosphere (ISA) model.

    Parameters:
        pressure_hpa (float): Pressure in hectopascals (hPa).

    Returns:
        float: Altitude in feet.
    """
    # Standard sea-level pressure in hPa
    sea_level_pressure = 1013.25

    # The exponent derived from the ISA barometric formula
    exponent = 0.1903

    # Conversion factor:
    # (T0 / L) in meters is approximately 44330.8 m, and 1 m = 3.28084 ft.
    # Thus, 44330.8 m * 3.28084 ft/m ≈ 145442 ft.
    conversion_factor = 145442

    # Calculate altitude in feet using the rearranged barometric formula
    altitude_feet = conversion_factor * (1 - (pressure_hpa / sea_level_pressure) ** exponent)

    return altitude_feet


def print_date_time(date_mode: int = 1):
    """
    Prints the current date/time information based on the selected mode.

    date_mode definitions:
        1: Print only time (HH:MM:SS).
        2: Print only date (YYYY-MM-DD).
        3: Print only day of the week.
        4: Print date and time.
        5: Print date, day of week, and time.
        6: Print only time (HH:MM:SS) without a newline at the end.
    
    Uses the RTC (PCF8523) to retrieve the current time.
    """
    
    # Lookup table for names of days (nicer printing).
    days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

    # Retrieve current date and time from RTC.
    t = rtc.datetime

    # Create formatted strings.
    date_str = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)
    time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    day_str = days[t.tm_wday]  # days is the global tuple defined earlier

    if DEBUG:
        if date_mode == 1:
            print(time_str)
        elif date_mode == 2:
            print(date_str)
        elif date_mode == 3:
            print(day_str)
        elif date_mode == 4:
            print("{} {}".format(date_str, time_str))
        elif date_mode == 5:
            print("{} {} {}".format(date_str, day_str, time_str))
        elif date_mode == 6:
            print(time_str, end='')
        elif date_mode == 7:
            print(time_str, end='')
        else:
            print("Invalid date", date_mode)

def get_uptime_seconds():
    """
    Returns the total time in seconds since power on or reset.
    Uses time.monotonic(), which is a monotonic clock that starts at 0.
    """
    return time.monotonic()

def seconds_to_hms(total_seconds):
    """
    Convert a number of seconds into a formatted string "HH:MM:SS",
    ensuring seconds are displayed as whole numbers.

    Args:
        total_seconds (int or float): Total number of seconds.

    Returns:
        str: The time formatted as "hours:minutes:seconds" with whole seconds.
    """
    total_seconds = int(total_seconds)  # Discard any decimal fraction
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return "{:02}:{:02}:{:02}".format(hours, minutes, seconds)

def initialization():
    # --- Erase entire display (VT100) ---
    #  ESC [ 2 J   → clear screen
    #  ESC [ H     → move cursor to home (optional)
    #  \x1b[{1};1H" → move cursor to top left
    print("\x1b[2J",end="")  # VT100 escapes codes
    # Move cursor to top-left (row 1, col 1)
    print(f"\x1b[{1};1H", end="") # VT100 escapes codes

    #log_to_sd software VERSION
    log_to_sd_version(VERSION)    
    # Take a referance pressure that the altiude is calculated 
    pressure_base = pressure_average(32)
    return pressure_base

def rtc_delay(x_seconds):
    """
    Adjusts the PCF8523 RTC back by x_seconds.

    Parameters:
      x_seconds (int or float): Number of seconds to subtract from the current RTC time.
      
    This function:
      1. Reads the current time from the RTC.
      2. Converts it to a Unix timestamp.
      3. Subtracts the specified seconds.
      4. Converts the adjusted timestamp back to a time tuple.
      5. Updates the RTC with the new time.
    """
    # Get the current RTC time. The datetime property typically returns a tuple:
    # (year, month, day, weekday, hours, minutes, seconds, subseconds)
    current_time = rtc.datetime

    # Convert the current time tuple to a Unix timestamp (ignoring subseconds).
    # time.mktime() requires a full struct_time tuple, so ensure your RTC provides one.
    current_timestamp = time.mktime(current_time)

    # Subtract the delay (in seconds) from the current timestamp.
    new_timestamp = current_timestamp - x_seconds

    # Convert the new timestamp back into a time tuple.
    new_time = time.localtime(new_timestamp)

    # Update the RTC with the new, adjusted time.
    rtc.datetime = new_time

    print("RTC delayed", x_seconds, "S")

def rtc_inc(x_seconds):
    """
    Increments the PCF8523 RTC by x_seconds.
    
    Parameters:
      x_seconds (int or float): Number of seconds to add to the current RTC time.
    
    Function Overview:
      1. Reads the current RTC time from the device.
      2. Converts the RTC time (a tuple) into a Unix timestamp using time.mktime.
      3. Increments the timestamp by the specified x_seconds.
      4. Converts the new timestamp back into a time tuple using time.localtime.
      5. Updates the RTC with the adjusted time.
    """
    # Retrieve the current time from the RTC.
    current_time = rtc.datetime

    # Convert the current time tuple to a Unix timestamp (seconds since epoch).
    current_timestamp = time.mktime(current_time)

    # Add x_seconds to the current timestamp.
    new_timestamp = current_timestamp + x_seconds

    # Convert the new timestamp back into a time tuple.
    new_time = time.localtime(new_timestamp)

    # Update the RTC with the new time tuple.
    rtc.datetime = new_time

    print("RTC incremented", x_seconds, "S")


def print_memory_usage():
    # Prints the amount of free and used memory in bytes.
    gc.collect()  # Run garbage collection to get an accurate reading
    free_mem = gc.mem_free()  # Get free memory
    allocated_mem = gc.mem_alloc()  # Get allocated memory
    total_mem = free_mem + allocated_mem  # Total memory available
    print("Memory Usage:")
    mem_used = allocated_mem
    mem_free = free_mem
    mem_total = total_mem
    mem_Kb_used =  mem_used/1000
    mem_Kb_free =  mem_free/1000  
    mem_Kb_total =  mem_total/1000      
    mem_used_percent = (mem_used / mem_total) * 100
    mem_free_percent = (mem_free / mem_total) * 100
    print(f"{mem_Kb_used:.1f} Kb {mem_used_percent:.1f}% used")
    print(f"{mem_Kb_free:.1f} Kb {mem_free_percent:.1f} % free")
    print(f"{mem_Kb_total:.1f} Kb total")

def print_cpu():
    # Prints CPU information including clock speed, unique ID, and CircuitPython version.
    board_name = os.uname().machine  # Get board name
    cpu_freq = microcontroller.cpu.frequency  # Get CPU frequency in Hz
    cpu_temp = microcontroller.cpu.temperature  # Get CPU temperature in Celsius

    print(f"{board_name}\n")    
    print(f"CPU Freq: {cpu_freq / 1_000_000:.2f} MHz")
    print(f"CPU Temp: {cpu_temp:.1f}°C {(cpu_temp * 9/5) + 32:.1f}°F")


def print_cpy():
    python_version = sys.version  # Get CircuitPython version
    os_version = os.uname().version  # Get CircuitPython OS version

    print(f"CPy V: {python_version}\n")
    print(f"OS V: {os_version}")


def print_start_up_message(delay=4.0):
    global ref_alt_ft
    global ref_loc
    global ref_num
    #ref_alt_ft_msl = 0
    #ref_alt_ft_home =1123    
    #ref_loc_hone = "Camas"
    #ref_loc_beach = "Beach"    

    if not sd_mounted:
        #  ESC [ 2 J   → clear screen
        #  ESC [ H     → move cursor to home (optional)
        #  \x1b[{1};1H" → move cursor to top left
        print("\x1b[2J",end="")  # VT100 escapes codes
        print("SD missing")
        while True:
            pass

    free_sd_mb = (sd_free_bytes()/(1024 * 1024))
    free_sd_gb = (sd_free_bytes()/(1024 * 1024 * 1024))

    gc.collect()  # Run garbage collection to get an accurate reading
    free_mem = gc.mem_free()  # Get free memory
    allocated_mem = gc.mem_alloc()  # Get allocated memory
    total_mem = free_mem + allocated_mem  # Total memory available
    mem_used = allocated_mem
    mem_free = free_mem
    mem_total = total_mem
    mem_Kb_used =  mem_used/1000
    mem_Kb_free =  mem_free/1000  
    mem_Kb_total =  mem_total/1000      
    mem_used_percent = (mem_used / mem_total) * 100
    mem_free_percent = (mem_free / mem_total) * 100
#    print(f"{mem_Kb_used:.1f} Kb {mem_used_percent:.1f}% used")
#    print(f"{mem_Kb_free:.1f} Kb {mem_free_percent:.1f} % free")
#    print(f"{mem_Kb_total:.1f} Kb total")

    python_version = sys.version  # Get CircuitPython version
    os_version = os.uname().version  # Get CircuitPython OS version
#    print(f"CPy V: {python_version}\n")
#    print(f"OS V: {os_version}")
#    print(sd_free_bytes())
#    print(free_sd_mb)
#    print(free_sd_gb)    

    for index in range(20):
        # Get RTC date and time
        t = rtc.datetime
        Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
        date_str = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)

        # --- Erase entire display (VT100) ---
        #  ESC [ 2 J   → clear screen
        #  ESC [ H     → move cursor to home (optional)
        print("\x1b[2J\x1b[H", end="")  # VT100 escapes codes

        # Move cursor to top-left (row 1, col 1)
        print(f"\x1b[{1};1H", end="") # VT100 escapes codes
        print("Kite Logger", f"V{VERSION:.2f}")
        print(f"{mem_Kb_free:.1f} Kb {mem_free_percent:.1f} % free")
        print("SD:", free_sd_gb, "GB") 
        print(Now_time_str, date_str)
        print(ref_loc, ref_alt_ft, "ft")
        battery_v = get_battery_voltage()
        print(f"Battery: {battery_v:.2f} V")
#        print(f"\x1b[{8};18H", "Red", end="") # VT100 escapes codes
        
        if check_relay_status():
            ref_alt_ft = ref_alt_ft_msl
            ref_loc = ref_loc_beach
            ref_num = 2
        if ref_num == 1:
            pixel_blink(1, 0.5, 255, 0, 0)
        else:
            pixel_blink(1, 0.5, 0, 255, 0)            


def print_mem_info():
# --- Erase entire display (VT100) ---
    #  ESC [ 2 J   → clear screen
    #  ESC [ H     → move cursor to home (optional)
    #  \x1b[{1};1H" → move cursor to top left
    print("\x1b[2J",end="")  # VT100 escapes codes
    print_memory_usage()
    pixel_blink(3, 1, 255, 0, 0)


def print_cpu_info():
# --- Erase entire display (VT100) ---
    #  ESC [ 2 J   → clear screen
    #  ESC [ H     → move cursor to home (optional)
    #  \x1b[{1};1H" → move cursor to top left
    print("\x1b[2J",end="")  # VT100 escapes codes
    print_cpu()
    pixel_blink(3, 1, 255, 0, 0)


def print_cpy_info():
# --- Erase entire display (VT100) ---
    #  ESC [ 2 J   → clear screen
    #  ESC [ H     → move cursor to home (optional)
    #  \x1b[{1};1H" → move cursor to top left
    print("\x1b[2J",end="")  # VT100 escapes codes
    print_cpy()
    pixel_blink(3, 1, 255, 0, 0)


# ----------------------------------------------------
# Initialization Code
# ----------------------------------------------------

# --- Initialize onboard NeoPixel ---
pixels.fill((0, 0, 0))

print_start_up_message()

# Clear screen
print("\x1b[2J",end="")  # VT100 escapes codes
# Move cursor to bottom-left (row 8, col 1)
print(f"\x1b[{1};1H", end="")

#set_bno055_calibration_values()
monitor_bno055_calibration()

pressure_base = initialization()

# ----------------------------------------------------
# Program Loop
# ----------------------------------------------------
while True:
    start = time.monotonic()
    sequence_num = sequence_num + 1

    # Get RTC date and time
    t = rtc.datetime
    Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    date_str = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)

    if Now_time_str == "00:00:00":
        pressure_base = initialization()
        sequence_num = 1

    if check_relay_status():
        mark_now = 1
        mark_count = mark_count + 1
        mark = mark_count
        cal_count = cal_count + 1
        if cal_count == 4:
            pressure_base = pressure_average(32)
    else:
        mark = 0
        cal_count = 0
        NeoPixel_LED((0, 0, 0))

    pressure = dps.pressure
    altitude = hpa_to_feet(pressure)
    altitude_above_gnd = hpa_to_feet(pressure) - hpa_to_feet(pressure_base)
    altitude_above_gnd_inches = altitude_above_gnd * 12.0
    current_feet = hpa_to_feet(pressure) - hpa_to_feet(pressure_base)
    current_alt_ft = ref_alt_ft + current_feet

    # Update feet maximum and minimum values
    if current_feet > max_feet:
        max_feet = current_feet
        t = rtc.datetime
        Hi_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    if current_feet < min_feet:
        min_feet = current_feet
        t = rtc.datetime
        Lo_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)

    # Total Time Operating
    tto = seconds_to_hms(get_uptime_seconds())

    battery_v = get_battery_voltage()
    bat_moving_avg = avg_bat_filter.update(battery_v)  # Get the updated moving average

    if battery_v < 2.8:
        NeoPixel_LED((0, 0, 0))
        while True:
           pass

    NOAA_pressure = dps310_to_noaa_inhg(pressure, altitude_above_gnd, dps.temperature)

    # Air flow measurements
    fs3000airflow = sensor_fs3000.airflow()
    airflow_mps = sensor_fs3000.airflow() 
    if airflow_mps is None:
        airflow_mps = previous_airflow
        air_error_cnt += 1
        air_error = air_error_cnt
    airflow_mph = airflow_mps * MPS_TO_MPH

    air_flow_moving_avg = avg_air_flow_filter.update(airflow_mph)

    # Update air flow maximum and minimum values
    if airflow_mph > max_airflow:
        max_airflow = airflow_mph
        t = rtc.datetime
        Hi_air_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    if airflow_mph < min_airflow:
        min_airflow = airflow_mph
        t = rtc.datetime
        Lo_air_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)

# Log BNO055 to SD card
    log_bno055_data_sd(Now_time_str)

    log_wind_data(airflow_mph)

# Log kite data to SD card
    log_summary_sd(Now_time_str, current_alt_ft)

# Log measurements to SD card
    log_to_sd(sequence_num,
        tto,
        mark,
        Now_time_str,
        current_alt_ft,
        pressure,
        altitude_above_gnd,
        max_feet,
        min_feet,
        NOAA_pressure,
        DSP310_temperature_f(),
        cpu_temperature_f(),
        battery_v,
        bat_moving_avg,
        airflow_mps,
        airflow_mph,
        air_flow_moving_avg,
        max_airflow,
        min_airflow,
        air_error
    )

    update_battery_voltage_color(bat_moving_avg)
    previous_airflow = airflow_mps
    air_error = 0
    
    # Wait until exactly 0.1 second has passed, measure & log every 1 sec.
    while time.monotonic() - start < 0.2:
        pass  # Just wait
    # The loop restarts exactly 0.1 second after 'start'
    NeoPixel_LED((0, 0, 0))

    if mark > 0:
        NeoPixel_LED((255, 0, 0))

    # Wait until exactly 1 second has passed, measure & log every 1 sec.
    while time.monotonic() - start < 1.0:
        pass  # Just wait
    # The loop restarts exactly 1 second after 'start'
    NeoPixel_LED((0, 0, 0))

