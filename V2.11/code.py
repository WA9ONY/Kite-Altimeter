# Kite Altimeter
# Version:
VERSION = 2.11
# Date: 2025-05-23
# Author: David Haworth, WA9ONY
# Website: https://www.qrz.com/db/WA9ONY
# GitHub https://github.com/WA9ONY/Adafruit-Feather/tree/main

# ----------------------------------------------------
# Kite Altimeter Hardware
# ----------------------------------------------------
# - Adafruit Feather RP2040 Adalogger - 8MB Flash with microSD Card - STEMMA QT / Qwiic
#     https://www.adafruit.com/product/5980
# - Adafruit FeatherWing OLED - 128x64
#     https://www.adafruit.com/product/4650
# - Adafruit DPS310 Precision Barometric Pressure / Altitude Sensor
#     https://www.adafruit.com/product/4494
# - Adafruit DS3231 Precision RTC - STEMMA QT
#     https://www.adafruit.com/product/5188 
# - Two Adafruit STEMMA QT / Qwiic JST SH 4-Pin Cable - 50mm Long
#     https://www.adafruit.com/product/4399
# - Adafruit Header Kit for Feather - 12-pin and 16-pin Female Header Set
#     https://www.adafruit.com/product/2886
# - FeatherWing Tripler
#     https://www.adafruit.com/product/3417
# - Adafruit Lithium Ion Polymer Battery Ideal For Feathers - 3.7V 400mAh
#     https://www.adafruit.com/product/3898

# ----------------------------------------------------
# Development Tools
# ----------------------------------------------------
# - Raspberry Pi 500 Rev 1.0 computer
# - OS: Debian GNU/Linux 12 (bookworm) aarch64 
# - Thonny IDE Version 4.1.4 Comes with Raspberry OS install. https://thonny.org/
# - Circup (for managing CircuitPython libraries) https://github.com/adafruit/circup
# - Circup is a Terminal CLI tool

# ----------------------------------------------------
# CircuitPython and Libraries
# ----------------------------------------------------
# - CircuitPython 9.2.4 https://circuitpython.org/board/adafruit_feather_rp2040/
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
import adafruit_dps310 # Advanced
import adafruit_ds3231
import adafruit_max1704x
import adafruit_displayio_sh1107
from i2cdisplaybus import I2CDisplayBus
from adafruit_pcf8523.pcf8523 import PCF8523


# ----------------------------------------------------
# Global Variables and Constants
# ----------------------------------------------------

TIME_ONLY = 1
DATE_ONLY = 2
DAY = 3
DATE_TIME = 4
DATE_DAY_TIME = 5
HI_NOW_LO_TIME = 6
TIME_ONLY_WITHOUT_NEWLINE = 7
BATTERY_STATUS = 8
CPU_TEMP = 9
RELAY_STATUS = 10
New_display = 11
SYSTEM_STATUS = 20

TIME_ALT_inHg_TEMP = 1
TIME_INCHES = 2
SEQ_FT_IN = 3
HPA_FT = 4
FT_MAX_MIN = 5

operating_mode = New_display
sequence_num = 0
SEA_LEVEL_PRESSURE = 1013.25  # Standard sea-level pressure in hPa
altitude_offset = 0
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

# Built-in NeoPixel setup
nexopixel_status = True
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # One NeoPixel
pixel.brightness = 0.5  # Adjust brightness (0.0 to 1.0)
neopixel_blink_time = 1

# Lookup table for names of days (nicer printing).
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


# ----------------------------------------------------
# Create Objects
# ----------------------------------------------------

# Connect to the card and mount the filesystem.
cs = digitalio.DigitalInOut(board.SD_CS)
sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Set up the ADC on A2 (Battery Voltage Monitor)
vbat_adc = analogio.AnalogIn(board.A0)

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
rtc = adafruit_ds3231.DS3231(i2c)

# Initialize sensor
dps = adafruit_dps310.DPS310(i2c)

# Set high oversampling for better accuracy
dps.pressure_oversample = 128  # Can be 1, 2, 4, 8, 16, 32, 64, or 128
dps.temperature_oversample = 2  # Improves temperature compensation

# Configure D4 as an input with an internal pull-up resistor.
pin = digitalio.DigitalInOut(board.D4)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP  # Ensures the pin reads high when not connected to ground.

# Initialize OLED
# SH1107 is vertically oriented 64x128
displayio.release_displays()
display_bus = I2CDisplayBus(board.I2C(), device_address=0x3C)
display = adafruit_displayio_sh1107.SH1107(display_bus, width=128, height=64)

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
    
    t = time.struct_time((2025, 3, 24, 11, 11, 0, 0, 83, 0))

    if DEBUG:
        print("Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t


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
    # Reads the battery voltage from A0 and converts it to real voltage.
    # ADC reference voltage (RP2040 uses a 3.3V reference)
    ADC_REF_VOLTAGE = 3.3
    # RP2040 ADC resolution is 16-bit, but only 12 bits are used (0-65535 range)
    ADC_RESOLUTION = 65535
    # Voltage divider ratio (from Feather RP2040's built-in circuit)
    VOLTAGE_DIVIDER_RATIO = 2.0  # The circuit divides by 2, so we multiply back
    CAL = 1.0712
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
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v2_" + date_now + ".txt"
    with open(file_name, "a") as f:
        f.write(" \n")
        f.write("***********************************************************************\n")
        f.write("* Pressure Altimeter Version %0.2f\n" % (verson))
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
        f.write(f"* Total {mem_Kb_total:.1f} Kb\n")
        f.write("*\n")
        
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
    file_name = "/sd/v2_" + date_now + ".txt"
    with open(file_name, "a") as f:
         f.write("* \n")
         f.write("* ----------------Measurements Logging----------------------------------------\n")
         f.write("*#, TTO, Mark,   Time,   Alt Ft, hPa, Dif Ft,  H Ft, L Ft, inHg, Temp, Tcpu, Vbat, VbatAv\n")

def log_to_sd(seq, tto, mark2, timest, p0, p1, p2, p3, p4, p4a, p5, p6, p7, p8):
    # Open file for append
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v2_" + date_now + ".txt"
    with open(file_name, "a") as f:
         f.write(
             "%d, %s, %d, %s,  %0.1f, %0.3f, %0.1f, %0.1f, %0.1f, %0.5f, %0.2f, %0.2f, %0.2f, %0.2f\n" %
             (seq, tto, mark2, timest, p0, p1, p2, p3, p4, p4a, p5, p6, p7, p8)
         )

def NeoPixel_LED(color=(255, 0, 0)): 
    # Red, green, blue
    # 0 is off, 255 is fully on
    pixel.fill(color)  # Turn NeoPixel on with specified color

def NeoPixel_Blink(millsec, color=(255, 0, 0)):
    """Blink the built-in NeoPixel for the given duration in milliseconds.
    
    Parameters:
        millsec (int): Duration of blink in milliseconds.
        color (tuple): RGB color for the NeoPixel.
    """
    if nexopixel_status: 
        pixel.fill((0, 0, 0))  # Ensure NeoPixel is off
        time.sleep(0.01)  # Small delay for visibility
        pixel.fill(color)  # Turn NeoPixel on with specified color
        time.sleep(millsec / 1000)  # Convert milliseconds to seconds
        pixel.fill((0, 0, 0))  # Turn NeoPixel off

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
    max_feet = 0
    min_feet = 0
    NeoPixel_LED((0, 255, 0))
    t = rtc.datetime
    date_now = "{}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday)
    file_name = "/sd/v2_" + date_now + ".txt"
    readings = []
    with open(file_name, "a") as f:
        f.write("*\n")              
        f.write("* Pressure reference calibration\n")    
    for i in range(measurements):
        print(".", end="")
        # Read the pressure measurement from the DPS310 sensor
        pressure_value = dps.pressure
        
        with open(file_name, "a") as f:
            f.write("* Measure %d %6.4f\n" % (i, pressure_value))

        readings.append(pressure_value)
        # Small delay between measurements for sensor stability
        time.sleep(0.1) # Delay for DPS310
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
    print("\n")
    print(f"Av: {avg_pressure:6.3f} hPa")
    print(f"Rng:{altitude_range_inches:6.3f} inches")
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
    # Retrieve current date and time from RTC.
    t = rtc.datetime

    # Create formatted strings.
    date_str = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)
    time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
    day_str = days[t.tm_wday]  # days is the global tuple defined earlier

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

def button_status():
    # If deep sleep is supported, use the alarm method.
    if hasattr(alarm, "exit_and_deep_sleep"):
        if alarm.wake_alarm:
            time.sleep(0.05)  # debounce delay
            if isinstance(alarm.wake_alarm, alarm.pin.PinAlarm):
                if alarm.wake_alarm.pin == board.D9:
                    return 9
                elif alarm.wake_alarm.pin == board.D6:
                    return 6
                elif alarm.wake_alarm.pin == board.D5:
                    return 5
            elif isinstance(alarm.wake_alarm, alarm.time.TimeAlarm):
                return 0

        # Deinitialize any existing digitalio button objects so alarms can use the pins.
        try:
            button9.deinit()
        except Exception:
            pass
        try:
            button6.deinit()
        except Exception:
            pass
        try:
            button5.deinit()
        except Exception:
            pass

        # Create PinAlarms for each button (active low with pull-ups) and a TimeAlarm.
        button9_alarm = alarm.pin.PinAlarm(pin=board.D9, value=False, pull=True)
        button6_alarm = alarm.pin.PinAlarm(pin=board.D6, value=False, pull=True)
        button5_alarm = alarm.pin.PinAlarm(pin=board.D5, value=False, pull=True)
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 1)

        # Enter deep sleep until one of the alarms triggers.
        alarm.exit_and_deep_sleep((button9_alarm, button6_alarm, button5_alarm, time_alarm))
    else:
        # Fallback polling method for boards that do not support deep sleep (e.g. RP2040).
        debounce_delay = 0.05  # 50 ms debounce delay

        # Create local digitalio button objects
        button9 = digitalio.DigitalInOut(board.D9)
        button9.direction = digitalio.Direction.INPUT
        button9.pull = digitalio.Pull.UP

        button6 = digitalio.DigitalInOut(board.D6)
        button6.direction = digitalio.Direction.INPUT
        button6.pull = digitalio.Pull.UP

        button5 = digitalio.DigitalInOut(board.D5)
        button5.direction = digitalio.Direction.INPUT
        button5.pull = digitalio.Pull.UP

        start = time.monotonic()
        while time.monotonic() - start < 1:
            # Check button on D9 pressed (active low)
            if not button9.value:
                time.sleep(debounce_delay)
                if not button9.value:
                    while not button9.value:
                        time.sleep(0.01)
                    # Deinitialize local buttons before returning
                    button9.deinit()
                    button6.deinit()
                    button5.deinit()
                    return 9
            # Check button on D6 pressed
            if not button6.value:
                time.sleep(debounce_delay)
                if not button6.value:
                    while not button6.value:
                        time.sleep(0.01)
                    button9.deinit()
                    button6.deinit()
                    button5.deinit()
                    return 6
            # Check button on D5 pressed
            if not button5.value:
                time.sleep(debounce_delay)
                if not button5.value:
                    while not button5.value:
                        time.sleep(0.01)
                    button9.deinit()
                    button6.deinit()
                    button5.deinit()
                    return 5
            time.sleep(0.01)
        # Deinitialize before returning if no button was pressed.
        button9.deinit()
        button6.deinit()
        button5.deinit()
        return 0

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

def get_uptime_seconds():
    # Returns the total time in seconds since power on or reset.
    # Uses time.monotonic(), which is a monotonic clock that starts at 0.
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

def sel_ref_alt(p1,p2):
    NeoPixel_LED(color=(0, 0, 255))
    start2 = time.monotonic()
    altitude = p1
    while time.monotonic() - start2 < 5.0:
        if check_relay_status():
            NeoPixel_LED(color=(255, 0, 0))
            altitude = p2
            return altitude
    return altitude

def initialization():
    # log_to_sd software VERSION
    log_to_sd_version(VERSION)
    ref_alt_ft = sel_ref_alt(ref_alt_ft_home, ref_alt_ft_msl)
    # Take a referance pressure that the altiude is calculated 
    pressure_base = pressure_average(32)
    print("Ref Alt Ft:", ref_alt_ft)
    # log_to_sd data column titles
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

print("Altimeter V", VERSION) 
print("Mode", operating_mode)
t = rtc.datetime
Cal_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)

#rtc_inc(1)
#rtc_delay(1)

pressure_base = initialization()

# ----------------------------------------------------
# Program Loop
# ----------------------------------------------------
while True:
    start = time.monotonic()  
    sequence_num = sequence_num + 1
    if check_relay_status():
        mark_count = mark_count + 1
        mark = mark_count
        NeoPixel_LED((255, 0, 0))
        cal_count = cal_count + 1
        print("Mark", mark_count)
        if cal_count == 4:
            print("Altimeter V", VERSION) 
            print("Mode", operating_mode)
            t = rtc.datetime
            Cal_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
            pressure_base = pressure_average(32)
            log_to_sd_header()
            max_feet = 0
            min_feet = 0
        SDcard_eject_halt = SDcard_eject_halt + 1
        if SDcard_eject_halt == 8:
            NeoPixel_LED((0, 0, 255))
            time.sleep(10.0)
            while not check_relay_status():
                time.sleep(1.0)
            pressure_base = pressure_average(32)
            log_to_sd_header()
    else:
        mark = 0
        cal_count = 0
        SDcard_eject_halt = 0
        NeoPixel_LED((0, 0, 0))    

    result = button_status()
    if result != 0:
        #print("Button status:", result)
        if result == 9:
            operating_mode = operating_mode + 1
            if operating_mode == 21:
               operating_mode = 0
        if result == 6:
            operating_mode = 6
        if result == 5:
            operating_mode = operating_mode - 1
            if operating_mode == 0:
               operating_mode = 20
        print("Mode:", operating_mode)

    LED_Blink(led_blink_time)
    NeoPixel_Blink(neopixel_blink_time, (0, 255, 0))  # Green Blink

    pressure = dps.pressure
    altitude = hpa_to_feet(pressure)
    altitude_above_gnd = hpa_to_feet(pressure) - hpa_to_feet(pressure_base)
    altitude_above_gnd_inches = altitude_above_gnd * 12.0
    current_feet = hpa_to_feet(pressure) - hpa_to_feet(pressure_base)
    current_alt_ft = ref_alt_ft + current_feet

    t = rtc.datetime
    Now_time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)

    # Update maximum and minimum values
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
    
    t = rtc.datetime
    # Create formatted strings.
    date_str = "{:04d}-{:02d}-{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday)
    time_str = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)

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
    LED_Blink(led_blink_time)
    
    if operating_mode == TIME_ALT_inHg_TEMP:
        # Operating Mode 1: Original functionality
        print_date_time(DATE_TIME)              # Print date and time
        print(f"{NOAA_pressure:.5f} inHg {DSP310_temperature_f():.1f} F")  # Print inHg and temp F        
        print("Altitude: %.1f""'" % current_alt_ft)  # Print altitude in feet
       
    elif operating_mode == TIME_INCHES:
        # Operating mode 2.
        print_date_time(TIME_ONLY_WITHOUT_NEWLINE)
        print(" %.1f"'"' %  altitude_above_gnd_inches) # Print altitude in inches

    elif operating_mode == SEQ_FT_IN:
        #Operating mode 3.
        print("#" + str(sequence_num), "%.1f""'" %  altitude_above_gnd, "%.1f"'"' %  altitude_above_gnd_inches)
        
    elif operating_mode == HPA_FT:
        # Operating mode 4.
        print("%.3f hPa" % pressure, "%.1f""'" %  altitude)    
        
    elif operating_mode == FT_MAX_MIN:
        # Operating Mode 5: Print current altitude (feet), maximum and minimum of all measurements.

        # Print the current, maximum, and minimum altitude measurements
        print("%.1f'" % current_feet, "%.1f'" % max_feet, "%.1f'" % min_feet)
        
    elif operating_mode == HI_NOW_LO_TIME:
        # Operating mode 6.
        print("H", Hi_time_str, "%.1f'" % max_feet)
        print("N", Now_time_str,"%.1f'" % current_feet)
        print("L", Lo_time_str, "%.1f'" % min_feet)
        
    elif operating_mode == 7:
        # Placeholder for future code for operating mode 7.
        battery_v = get_battery_voltage()
        print(battery_v)
        
    elif operating_mode == BATTERY_STATUS:
        # Placeholder for future code for operating mode 8.
        battery_v = get_battery_voltage()
        print(battery_v)        
        
    elif operating_mode == CPU_TEMP:
        # Placeholder for future code for operating mode 9.
        print("CPU Temp: ", cpu_temperature_f())
        
    elif operating_mode == RELAY_STATUS:
        # Placeholder for future code for operating mode 10. 
        print("Relay status: ", check_relay_status())

    elif operating_mode == New_display:
        # Placeholder for future code for operating mode 11.
        print("Max", Hi_time_str, "%.1f'" % max_feet)
        print("Now", Now_time_str, "%.1f""'" % current_alt_ft)
#        print("Alt: %.1f""'" % current_alt_ft)  # Print altitude in feet
        battery_v = get_battery_voltage()
#        print(battery_v)
        print("CT ", Cal_time_str, "%.2fV" % battery_v)

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
    elif operating_mode == SYSTEM_STATUS:
        # Placeholder for future code for operating mode 20.
        print("Initializing\nKite hPa Altimeter")
        print("Version", VERSION)
        print("Close Alt Case 4 Cal")  # Time to put the case lid on
        time.sleep(pause_time*3)
        print_date_time(3)
        print_date_time(2)
        print_date_time(1)
        time.sleep(pause_time*3) 
        print_memory_usage()
        time.sleep(pause_time*3)
        print_cpu_info()

        measurements_num = 8 
        pressure_base = pressure_average(measurements_num)
        time.sleep(pause_time)
        print(
            "Found MAX1704x with chip version",
            hex(max17.chip_version),
            "and id",
            hex(max17.chip_id),
        )
        
    else:
        print("Invalid", operating_mode)

# Wait until exactly 1 second has passed, measure & log every 1 sec.
    while time.monotonic() - start < 1.0:
        pass  # Just wait
    # The loop restarts exactly 1 second after 'start'
    
   