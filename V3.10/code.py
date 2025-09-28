# Pressure Altimeter
# Version:
VERSION = 3.10
# Date: 2025-04-23
# Author: David Haworth, WA9ONY
# Website: https://www.qrz.com/db/WA9ONY
# GitHub https://github.com/WA9ONY/Adafruit-Feather/tree/main

# ----------------------------------------------------
# Kite Altimeter Hardware
# ----------------------------------------------------
# - Adafruit Metro RP2350
#     https://www.adafruit.com/product/6267
#     32 GB microSD card plugged into the Metro RP2350
# - Adafruit 2.8" TFT Touch Shield for Arduino with Resistive Touch Screen v2 - STEMMA QT / Qwiic
#     https://www.adafruit.com/product/1651
# - Adafruit DPS310 Precision Barometric Pressure / Altitude Sensor
#     https://www.adafruit.com/product/4494
#     I2C to Metro RP2350
# - Adafruit DS3231 Precision RTC - STEMMA QT
#     https://www.adafruit.com/product/5188
#     I2C to Metro RP2350
# - Two Adafruit STEMMA QT / Qwiic JST SH 4-Pin Cable - 50mm Long
#     https://www.adafruit.com/product/4399
# - Adafruit Swirly Aluminum Mounting Grid for 0.1" Spaced PCBs - 10x5
#     https://www.adafruit.com/product/5774


# ----------------------------------------------------
# Development Tools
# ----------------------------------------------------
# - OpenAI ChatGPT
# - Raspberry Pi 500 Rev 1.0 computer
# - OS: Debian GNU/Linux 12 (bookworm) aarch64 
# - Thonny IDE Version 4.1.4 Comes with Raspberry OS install. https://thonny.org/
# - Circup (for managing CircuitPython libraries) https://github.com/adafruit/circup
# - Circup is a Terminal CLI tool

# ----------------------------------------------------
# CircuitPython and Libraries
# ----------------------------------------------------
# - CircuitPython 9.2.7 https://circuitpython.org/board/adafruit_feather_rp2040/
# - CircuitPython 9.X Libraries https://circuitpython.org/libraries

# ----------------------------------------------------
# Modules and Libraries
# ----------------------------------------------------
import os
import gc
import sys
import math
import time
import board
import busio
import storage
import analogio
import neopixel
import digitalio
import displayio
import terminalio
import adafruit_sdcard
import microcontroller
import adafruit_dps310 # Advanced
import adafruit_ds3231 # RTC
import adafruit_ili9341
from fourwire import FourWire
from adafruit_display_text import label


# ----------------------------------------------------
# Global Variables and Constants
# ----------------------------------------------------

DEBUG = True  # True and False
DEBUG1 = False 
DEBUG2 = False

degree_symbol = "\u00B0"

TIME_ONLY = 1
HI_NOW_LO_TIME = 2
DAY = 3
DATE_TIME = 4
DATE_DAY_TIME = 5
TIME_ONLY_WITHOUT_NEWLINE = 7
BATTERY_STATUS = 8
RELAY_STATUS = 10
SYSTEM_STATUS = 20

TIME_ALT_inHg_TEMP= 1
TIME_INCHES = 2
SEQ_FT_IN = 3
HPA_FT = 4
FT_MAX_MIN = 5

operating_mode = 3

sequence_num = 0
SEA_LEVEL_PRESSURE = 1013.25  # Standard sea-level pressure in hPa
altitude_offset = 0  # Offset for zeroing altitude
pause_time = 0.01
mark_count = 0
cal_count = 0
SDcard_eject_halt = 0

ref_alt_ft_msl = 0
ref_alt_ft_home = 1123
ref_alt_ft = ref_alt_ft_home

max_feet = 0
min_feet = 0

Hi_time_str = ""
Lo_time_str = ""

pause_time = 0.5

# Built-in LED setup
led_status = True
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led_blink_time = 50 # milliseconds

# Lookup table for names of days (nicer printing).
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


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

# The SD_CS pin is the chip select line.
SD_CS = board.SD_CS
# Connect to the card and mount the filesystem.

# Connect to the card and mount the filesystem.
cs = digitalio.DigitalInOut(SD_CS)
sdcard = adafruit_sdcard.SDCard(busio.SPI(board.SD_SCK, board.SD_MOSI, board.SD_MISO), cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
rtc = adafruit_ds3231.DS3231(i2c)

# Initialize sensor
dps = adafruit_dps310.DPS310(i2c)

# Set high oversampling for better accuracy
dps.pressure_oversample = 128  # Can be 1, 2, 4, 8, 16, 32, 64, or 128
dps.temperature_oversample = 2  # Improves temperature compensation

# Release any resources currently in use for the displays
displayio.release_displays()

# Use Hardware SPI
spi = board.SPI()

tft_cs = board.D10
tft_dc = board.D9

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

class MovingAverage:
    def __init__(self, window_size=16):
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

# Create an instance of the filter with a window size of 16.
avg_filter = MovingAverage(16)

# Set date & time if needed
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
    
    t = time.struct_time((2025, 4, 14, 15, 9, 0, 0, 104, 0))

    if DEBUG:
        print("Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t
    print(rtc.datetime)
    while True:
        pass


# ----------------------------------------------------
# Functions
# ----------------------------------------------------

def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " bytes"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print("{0:<40} Size: {1:>10}".format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

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
    # Reads the battery voltage from A0 and converts it to real voltage.
    # ADC reference voltage (RP2040 uses a 3.3V reference)
    ADC_REF_VOLTAGE = 3.3
    # RP2040 ADC resolution is 16-bit, but only 12 bits are used (0-65535 range)
    ADC_RESOLUTION = 65535
    # Voltage divider ratio (from Feather RP2040's built-in circuit)
    VOLTAGE_DIVIDER_RATIO = 2.0  # The circuit divides by 2, so we multiply back
    CAL = 1.03934
    raw_value = vbat_adc.value  # Read ADC value (0-65535)
    measured_voltage = (raw_value / ADC_RESOLUTION) * ADC_REF_VOLTAGE
    battery_voltage = measured_voltage * VOLTAGE_DIVIDER_RATIO * CAL  # Compensate for voltage divider
    return battery_voltage

def check_relay_status():
    # When the relay closes, D4 is connected to ground and reads low (False).
    # Return True if the pin reads 0.
    return not pin.value

def cpu_temperature_f():
    # Returns the current RP2040 internal temperature in Fahrenheit.
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

def log_to_sd_version(verson):
    # Open file for append
    t = rtc.datetime
    now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
#   date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    date_now = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)
    date_time = "* " + date_now + " " + now_time_str + "\n"
    file_name = "/sd/v3_" + date_now + ".txt"
    with open(file_name, "a") as f:
        f.write("* \n")
        f.write(date_time)
        f.write("* Pressure Altimeter Version %0.2f\n" % (verson))
        f.write("* \n")
    
        print("* \n")
        print(date_time)         
        print("* Pressure Altimeter Version %0.2f\n" % (verson))
        print("* \n")
        time.sleep(4)
        
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
        f.write(f"* Total {mem_Kb_total:.1f} Kb\n")

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

def log_to_sd_header():
    # Open file for append
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v3_" + date_now + ".txt"
    with open(file_name, "a") as f:
         f.write("* \n")
         f.write("* ----------------Measurements Logging--------------------------------------------------------\n")
         f.write("* Nr, TTO, Mark,   Time,   Alt Ft, hPa, Dif Ft,  H Ft, L Ft, inHg, Temp, Tcpu, Vbat, VbatAv\n")

def log_to_sd(seq, tto, mark2, timest, p0, p1, p2, p3, p4, p4a, p5, p6, p7, p8):
    # Open file for append
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v3_" + date_now + ".txt"
    with open(file_name, "a") as f:
         f.write(
             "%d, %s, %d, %s,  %0.1f, %0.3f, %0.1f, %0.1f, %0.1f, %0.3f, %0.2f, %0.2f, %0.2f, %0.2f\n" %
             (seq, tto, mark2, timest, p0, p1, p2, p3, p4, p4a, p5, p6, p7, p8)
         )

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
#    print("Battery Voltage: {:.2f} V => Level {} => Color {}".format(battery_voltage, level, color))

"""
# Example usage:
# This test loop cycles through voltages from 3.0V to 4.2V to simulate battery levels.
test_voltages = [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.1, 4.2]
for voltage in test_voltages:
    update_battery_voltage_color(voltage)
    time.sleep(2)
"""

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


def LED_Blink(millsec):
    # Blink the built-in LED for the given duration in milliseconds.
    if led_status: 
        led.value = False  # Ensure LED is off
        time.sleep(0.05)  # Small delay to ensure it's seen as an intentional blink
        led.value = True  # Turn LED on
        time.sleep(millsec / 1000)  # Convert milliseconds to seconds
        led.value = False  # Turn LED off

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

def pressure_average(measurements: int = 64) -> float:
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
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v3_" + date_now + ".txt"

    if DEBUG:
        print("Base hPa cal", measurements,"rdg")
    readings = []
    with open(file_name, "a") as f:
        f.write("*\n")              
        f.write("* Pressure reference calibration\n")    
    for i in range(measurements):
        if DEBUG:
            print(".", end="")
        # Read the pressure measurement from the DPS310 sensor
        pressure_value = dps.pressure
        
        with open(file_name, "a") as f:
            f.write("* Measure %d %6.4f\n" % (i, pressure_value))

        readings.append(pressure_value)
    if DEBUG:
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

    with open(file_name, "a") as f:
        f.write("*\n")
        f.write("* Pressure Calibration Summary\n")
        f.write("* Number of measurements %d\n" % (measurements))
        f.write("* Average hPa %6.3f\n" % (avg_pressure))
        f.write("* Minimum hPa %6.3f\n" % (min_pressure))
        f.write("* Maximum hPa %6.3f\n" % (max_pressure))
        f.write("* Standard deviation hPa %6.3f\n" % (std_dev))
        f.write("* Range in hPa %6.3f\n" % (pressure_range))
        f.write("* Range in inches %6.3f\n" % (altitude_range_inches))
        f.write("* Reference Altitude in feet %7.3f\n" % (ref_alt_ft))
    NeoPixel_LED((0, 0, 0))
    return avg_pressure

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
    
def battery_monitor():
    # Quick starting allows an instant 'auto-calibration' of the battery. However, its a bad idea
    # to do this right when the battery is first plugged in or if there's a lot of load on the battery
    # so uncomment only if you're sure you want to 'reset' the chips charge calculator.
    # print("Quick starting")
    # max17.quick_start = True
    voltage = max17.cell_voltage
    soc = max17.cell_percent
    rate = max17.charge_rate
 
    print(f"Battery: {voltage:.2f} V")
    print(f"Battery: {max17.cell_percent:.1f} %")
    print(f"Chrg rate: {max17.charge_rate:.1f} %/hr")
    
    # Only estimate runtime if discharging

    if rate < 0:
        runtime_hours = soc / abs(rate)
        print(f"Est runtime: {runtime_hours:.1f} hrs")
    else:
        print("Battery charging/idle.")
    print("")

def print_chip_temperature():
    # Reads and prints the RP2040 chip temperature in Fahrenheit.
    temperature_c = microcontroller.cpu.temperature  # Read temperature in Celsius
    temperature_f = (temperature_c * 9 / 5) + 32  # Convert to Fahrenheit
    print(f"Chip: {temperature_f:.2f} °F")

def print_memory_usage():
    # Prints the amount of free and used memory in bytes.
    gc.collect()  # Run garbage collection to get an accurate reading
    free_mem = gc.mem_free()  # Get free memory
    allocated_mem = gc.mem_alloc()  # Get allocated memory
    total_mem = free_mem + allocated_mem  # Total memory available
    print("Memory Usage:\n\n")
    time.sleep(pause_time*3)
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
    time.sleep(pause_time*5)
    
def print_cpu_info():
    # Prints CPU information including clock speed, unique ID, and CircuitPython version.
    cpu_freq = microcontroller.cpu.frequency  # Get CPU frequency in Hz
    cpu_temp = microcontroller.cpu.temperature  # Get CPU temperature in Celsius
    unique_id = microcontroller.cpu.uid  # Get the unique ID of the chip
    python_version = sys.version  # Get CircuitPython version
    board_name = os.uname().machine  # Get board name
    os_version = os.uname().version  # Get CircuitPython OS version

    # Format the unique ID separately before printing
    unique_id_str = " ".join(["{:02X}".format(x) for x in unique_id])

    print(f"{board_name}\n")
    time.sleep(pause_time*4)    
    print(f"CPU Freq: {cpu_freq / 1_000_000:.2f} MHz")
    print(f"CPU Temp: {cpu_temp:.1f}°C {(cpu_temp * 9/5) + 32:.1f}°F")
    time.sleep(pause_time*3)
    print(f"ID: {unique_id_str}\n")
    time.sleep(pause_time*3)
    print(f"CPy V: {python_version}")
    time.sleep(pause_time*4)
    print(f"OS V: {os_version}")
    time.sleep(pause_time*4)


def battery_percentage():
    # Retrieve the current battery voltage
    voltage = get_battery_voltage()
    
    # Define the voltage limits for 0% and 100%
    V_MIN = 3.3   # 0%
    V_MAX = 4.2  # 100%
    
    # Calculate the percentage using linear interpolation
    percent = (voltage - V_MIN) / (V_MAX - V_MIN) * 100

    # Clamp the result between 0 and 100
    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100
        
    return percent

def estimate_remaining_time(battery_voltage, time_on_hours, temperature):
    """
    Estimate the remaining operating time (in hours) of a LiPo battery.
    
    Parameters:
      battery_voltage (float): The current battery voltage (volts).
      time_on_hours (float): Total time since power on (hours).
      temperature (float): The current temperature (°C).
      
    Returns:
      float: Estimated remaining operating time in hours.
    """
    # Battery and load parameters
    capacity_mAh = 420.0      # Battery capacity in milliamp-hours
    current_draw_mA = 41.0    # Constant circuit current draw in mA
    
    # Define LiPo voltage thresholds (approximate)
    v_min = 3.3   # Voltage at which battery is considered empty
    v_max = 4.2   # Voltage at which battery is considered fully charged
    
    # 1. Estimate remaining capacity based on voltage reading.
    #    Here we assume a linear mapping (for demonstration only).
    soc_voltage = (battery_voltage - v_min) / (v_max - v_min)
    # Clamp the state-of-charge (SOC) between 0 (empty) and 1 (full)
    if soc_voltage > 1:
        soc_voltage = 1
    elif soc_voltage < 0:
        soc_voltage = 0
    remaining_capacity_voltage = soc_voltage * capacity_mAh
    
    # 2. Estimate remaining capacity using coulomb counting.
    #    Assumes battery was full at power-on.
    used_capacity = current_draw_mA * time_on_hours
    remaining_capacity_coulomb = capacity_mAh - used_capacity
    
    # Combine the two estimates (here we simply average them).
    remaining_capacity = (remaining_capacity_voltage + remaining_capacity_coulomb) / 2.0
    
    # Ensure we don't report negative remaining capacity.
    if remaining_capacity < 0:
        remaining_capacity = 0
    
    # Calculate estimated remaining time (in hours)
    estimated_time_hours = remaining_capacity / current_draw_mA
    
    # 3. Apply a simple temperature compensation.
    #    For example, if temperature is below 15°C, reduce estimated time.
    if temperature < 15:
        # For every 10°C below 15°C, reduce effective time by 10%
        reduction_factor = ((15 - temperature) / 10) * 0.1
        estimated_time_hours *= (1 - reduction_factor)
    
    return estimated_time_hours

def sel_ref_alt(p1,p2):
    NeoPixel_LED(color=(0, 0, 255))
    start2 = time.monotonic()
    altitude = p1
    while time.monotonic() - start2 < 5.0:
        pass  # Just wait
    return altitude

def initialization():
    # log_to_sd software VERSION
    log_to_sd_version(VERSION)
#    ref_alt_ft = sel_ref_alt(ref_alt_ft_home, ref_alt_ft_msl)
    # Take a referance pressure that the altiude is calculated 
    pressure_base = pressure_average(32)
    # log_to_sd data column titles
    log_to_sd_header()
    return pressure_base


# ----------------------------------------------------
# Initialization Code
# ----------------------------------------------------

print("Altimeter V", VERSION)
print("Display Mode", operating_mode)

#print_directory("/sd", 0)

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

    if (Now_time_str == "00:00:00") or (Now_time_str == "00:00:01") or (Now_time_str == "00:00:03"):
        pressure_base = initialization()
        sequence_num = 1
        time.sleep(4)

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
    mark = -1
    battery_v = -1
    bat_moving_avg = -1
    
    NOAA_pressure = dps310_to_noaa_inhg(pressure, altitude_above_gnd, dps.temperature)

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
        bat_moving_avg
    )

    if DEBUG1:
        print(sequence_num,
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
        bat_moving_avg
        )    

    if operating_mode == TIME_ALT_inHg_TEMP:
        # Operating Mode 1: Original functionality
        print_date_time(DATE_TIME)              # Print date and time
        print(f"Pressure: {NOAA_pressure:.5f} inHg, Temperature {DSP310_temperature_f():.1f} F")  # Print inHg and temp F        
        print("Altitude: %.1f""'" % current_alt_ft)  # Print altitude in feet
        print()
        
    elif operating_mode == HI_NOW_LO_TIME:
        # Operating mode 2.
        print("H", Hi_time_str, "%.1f'" % max_feet)
        print("N", Now_time_str,"%.1f'" % current_feet)
        print("L", Lo_time_str, "%.1f'" % min_feet)

    elif operating_mode == 3:
        #Operating mode 3.
        print_date_time(DATE_TIME)              # Print date and time
        print(f"Pressure: {NOAA_pressure:.5f} inHg, Temperature {DSP310_temperature_f():.1f} F")  # Print inHg and temp F        
        print("Altitude: %.1f""'" % current_alt_ft)  # Print altitude in feet
        print("H", Hi_time_str, "%.1f'" % max_feet)
        print("N", Now_time_str,"%.1f'" % current_feet)
        print("L", Lo_time_str, "%.1f'" % min_feet)
        print()
        
    elif operating_mode == HPA_FT:
        # Operating mode 4.
        print("%.3f hPa" % pressure, "%.1f""'" %  altitude)    
        print("#" + str(sequence_num), "%.1f""'" %  altitude_above_gnd, "%.1f"'"' %  altitude_above_gnd_inches)
        
    elif operating_mode == FT_MAX_MIN:
        # Operating Mode 5: Print current altitude (feet), maximum and minimum of all measurements.
        # Print the current, maximum, and minimum altitude measurements
        print("%.1f'" % current_feet, "%.1f'" % max_feet, "%.1f'" % min_feet)
        
    elif operating_mode == 6:
        # Placeholder for future code for operating mode 6.
        pass
    elif operating_mode == 7:
        # Placeholder for future code for operating mode 7.
        pass     
    elif operating_mode == BATTERY_STATUS:
        # Placeholder for future code for operating mode 8.
        pass
    elif operating_mode == 9:
        # Placeholder for future code for operating mode 9.
        pass        
    elif operating_mode == 10:
        # Placeholder for future code for operating mode 10.
        pass
    elif operating_mode == 11:
        # Placeholder for future code for operating mode 11.
        pass
    elif operating_mode == 12:
        # Placeholder for future code for operating mode 12.
        pass
    elif operating_mode == 13:
        # Placeholder for future code for operating mode 13.
        pass
    elif operating_mode == 14:
        # Placeholder for future code for operating mode 14.
        pass
    elif operating_mode == 15:
        # Placeholder for future code for operating mode 15.
        pass
    elif operating_mode == 16:
        # Placeholder for future code for operating mode 16.
        pass
    elif operating_mode == 17:
        # Placeholder for future code for operating mode 17.
        pass
    elif operating_mode == 18:
        # Placeholder for future code for operating mode 18.
        pass
    elif operating_mode == 19:
        # Placeholder for future code for operating mode 19.
        pass
    elif operating_mode == 20:
        # Placeholder for future code for operating mode 20
        pass
    else:
        print("Invalid", operating_mode)

    # Wait until exactly 0.1 second has passed, measure & log every 1 sec.
    while time.monotonic() - start < 0.01:
        pass  # Just wait
    # The loop restarts exactly 0.1 second after 'start'
    NeoPixel_LED((0, 0, 0))

#    if mark > 0:
#        NeoPixel_LED((255, 0, 0))
#        print("Mark", mark)
    NeoPixel_LED((0, 255, 0))
    # Wait until exactly 1 second has passed, measure & log every 1 sec.
    while time.monotonic() - start < 1.0:
        pass  # Just wait
    # The loop restarts exactly 1 second after 'start'
    NeoPixel_LED((0, 0, 0))


