# Kite Altimeter
# Version:
VERSION = 4.12
# Date: 2025-04-26
# Author: David Haworth, WA9ONY
# Website: https://www.qrz.com/db/WA9ONY
# GitHub https://github.com/WA9ONY/Adafruit-Feather/tree/main

# ----------------------------------------------------
# Kite Altimeter Hardware
# ----------------------------------------------------
# - Adafruit Feather RP2040 Adalogger - 8MB Flash with microSD Card - STEMMA QT / Qwiic
#     https://www.adafruit.com/product/5980
# - Adafruit DPS310 Precision Barometric Pressure / Altitude Sensor
#     https://www.adafruit.com/product/4494
# - Two Adafruit STEMMA QT / Qwiic JST SH 4-Pin Cable - 50mm Long
#     https://www.adafruit.com/product/4399
# - Adafruit DS3231 Precision RTC - STEMMA QT + SD
#     https://www.adafruit.com/product/5188 
# - Lithium Ion Polymer Battery - 3.7V 350mAh
#     https://www.adafruit.com/product/2750
#     Altimeter runs for 14 hours 

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
#import adafruit_displayio_sh1107
#from i2cdisplaybus import I2CDisplayBus
#from adafruit_dps310.basic import DPS310
import adafruit_dps310 # Advanced

# ----------------------------------------------------
# Global Variables and Constants
# ----------------------------------------------------
DEBUG = False  # True and False
DEBUG1 = False 
DEBUG2 = False

sequence_num = 0
SEA_LEVEL_PRESSURE = 1013.25  # Standard sea-level pressure in hPa
altitude_offset = 0  # Offset for zeroing altitude
pause_time = 0.01
mark_count = 0
cal_count = 0
SDcard_eject_halt = 0

ref_alt_ft_msl = 0
ref_alt_ft_home = 1123
ref_alt_ft_CannonBeachOR = 8
ref_alt_ft = ref_alt_ft_CannonBeachOR

Hi_time_str = ""
Lo_time_str = ""
max_feet = 0
min_feet = 0
pause_time = 1

# Built-in LED setup
led_status = True
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led_blink_time = 50 # milliseconds


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


# Connect to the SD card and mount the filesystem.
cs = digitalio.DigitalInOut(board.SD_CS)
sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Set up the ADC on A2 (Battery Voltage Monitor)
vbat_adc = analogio.AnalogIn(board.A0)

# i2c = board.I2C()  # uses board.SCL and board.SDA
i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
rtc = adafruit_ds3231.DS3231(i2c)

# Initialize I2C and sensor
#i2c = busio.I2C(board.SCL, board.SDA)
dps = adafruit_dps310.DPS310(i2c)

# Set high oversampling for better accuracy
dps.pressure_oversample = 128  # Can be 1, 2, 4, 8, 16, 32, 64, or 128
dps.temperature_oversample = 2  # Improves temperature compensation

# Configure D4 as an input with an internal pull-up resistor.
pin = digitalio.DigitalInOut(board.D4)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP  # Ensures the pin reads high when not connected to ground.

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
    
    t = time.struct_time((2025, 3, 24, 11, 11, 0, 0, 83, 0))

    if DEBUG:
        print("Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t

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


# ----------------------------------------------------
# Functions
# ----------------------------------------------------

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
    return not pin.value

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

def log_to_sd_version(verson):
    # open file for append
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v4_" + date_now + ".txt"
    with open(file_name, "a") as f:
        f.write(" \n")
        f.write("***********************************************************************\n")
        f.write("* Pressure Altimeter Verson %0.2f\n" % (verson))
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

def log_to_sd_header():
    # open file for append
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v4_" + date_now + ".txt"
    with open(file_name, "a") as f:
         f.write("* \n")
         f.write("* ----------------Measurements Logging--------------------------------------------------------\n")
         f.write("* Nr, TTO, Mark,   Time,   Alt Ft, hPa, Dif Ft,  H Ft, L Ft, inHg, Temp, Tcpu, Vbat, VbatAv\n")

def log_to_sd(seq, tto, mark2, timest, p0, p1, p2, p3, p4, p4a, p5, p6, p7, p8):
    # open file for append
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v4_" + date_now + ".txt"
    with open(file_name, "a") as f:
         f.write(
             "%d, %s, %d, %s,  %0.1f, %0.3f, %0.1f, %0.1f, %0.1f, %0.5f, %0.2f, %0.2f, %0.2f, %0.2f\n" %
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
    """Blink the built-in LED for the given duration in milliseconds."""
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
    file_name = "/sd/v4_" + date_now + ".txt"

    if DEBUG:
        print("Base hPa cal", measurements,"rdg")
    readings = []
    with open(file_name, "a") as f:
        f.write("*\n")              
        f.write("* Pressure referance calibration\n")    
    for i in range(measurements):
        if DEBUG:
            print(".", end="")
        # Read the pressure measurement from the DPS310 sensor
        pressure_value = dps.pressure
        
        with open(file_name, "a") as f:
            f.write("* Measure %d %6.4f\n" % (i, pressure_value))

        readings.append(pressure_value)
        # Small delay between measurements for sensor stability
        time.sleep(0.1) # Delay for DPS310
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
        f.write("* Standand deviation hPa %6.3f\n" % (std_dev))
        f.write("* Range in hPa %6.3f\n" % (pressure_range))
        f.write("* Range in inches %6.3f\n" % (altitude_range_inches))
        f.write("* Referance Altitude in feet %7.3f\n" % (ref_alt_ft))
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

def initialization():
    #log_to_sd software VERSION
    log_to_sd_version(VERSION)    
    # Take a referance pressure that the altiude is calculated 
    pressure_base = pressure_average(32)
    #log_to_sd data column titles
    log_to_sd_header()
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


# ----------------------------------------------------
# Initialization Code
# ----------------------------------------------------
if DEBUG:
    print("Initializing\nKite hPa Altimeter")
    print("Version", VERSION)
"""
# Adjust RTC
rtc_inc(4)
#rtc_delay(1)
while True:
    t = rtc.datetime
    Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    print(Now_time_str)
    time.sleep(0.5)
"""

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
        mark_count = mark_count + 1
        mark = mark_count
#        NeoPixel_LED((255, 0, 0))
        cal_count = cal_count + 1
        if cal_count == 4:
            pressure_base = pressure_average(32)
            log_to_sd_header()
        SDcard_eject_halt = SDcard_eject_halt + 1
        if SDcard_eject_halt == 8:
            NeoPixel_LED((0, 0, 255))
            time.sleep(10.0)
            while not check_relay_status():
                time.sleep(1.0)
            pressure_base = pressure_average(32)
            log_to_sd_header()
            max_feet = 0
            min_feet = 0
    else:
        mark = 0
        cal_count = 0
        SDcard_eject_halt = 0
        NeoPixel_LED((0, 0, 0))

#    pressure = dps310.pressure
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
    bat_moving_avg = avg_filter.update(battery_v)  # Get the updated moving average

    if battery_v < 2.8:
        NeoPixel_LED((0, 0, 0))
        while True:
           pass

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
    # Clink red LED after writing data to SD card
#    LED_Blink(led_blink_time)

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

    if DEBUG2:
        print("H", Hi_time_str, "%.1f'" % max_feet)
        print("N", Now_time_str,"%.1f'" % current_feet)
        print("L", Lo_time_str, "%.1f'" % min_feet)
        print("New battery value: {:.2f}, Battery filtered average: {:.2f}".format(battery_v, bat_moving_avg))

    update_battery_voltage_color(bat_moving_avg)

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
