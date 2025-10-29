<P align="center"> - <A HREF="https://www.qrz.com/db/WA9ONY">WA9ONY</A> - <A HREF="https://www.youtube.com/@Kites-Flying">YouTube Kites-Flying</A> - <A HREF="https://www.youtube.com/user/DavidAHaworth">YouTube David Haworth</A> - <A HREF="http://www.stargazing.net/david/index.html">Website</A> -
</P> 

</P> 
<p align="center"> <img width="588" height="588" src="/Images/V7top.JPEG">
</p>

Raspberry Pi 5 with the 5" touch display 2 connected to INIU USB 10ah battery bank.

# Kite Altimeter Base Station V7

+ Version 7 was created to be a ground station monitoring the change of the barometric pressure during the flight time and is currently under development. V7 is based on the Raspberry Pi 5 with 5" touch display.
+ V7 is a Raspberry Pi 5 with touch display.

<TABLE>
<TR>
<TD><P><B>
 HW
 </B></P></TD>
<TD><P><B>
 Weight
 </B></P></TD>
<TD><P><B>
 Size
 </B></P></TD>
<TD><P><B>
 Battery
 </B></P></TD>
<TD><P><B>
 uC 
 </B></P></TD>
<TD><P><B>
 SW 
 </B></P></TD>
<TD><P><B>
 Display 
 </B></P></TD>
<TD><P><B>
 RTC
 </B></P></TD>
<TD><P><B>
 Altitude<BR>Temp. 
 </B></P></TD>
</TR>

<TR>
<TD>
 V7
</TD>
<TD>
 451 g<BR>15.91&nbspoz. 
</TD>
<TD>
 3.6"&nbspx<BR>5.65"&nbspx<BR>2.26"
</TD> 
<TD>
 <A HREF="https://www.amazon.com/dp/B0CB1FW5FC?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1">5V INIU Ultra Slim 10000mAh</A>
</TD>
<TD>
 <A HREF="https://www.adafruit.com/product/5813">Raspberry Pi 5 - 8 GB RAM</A> 
</TD>
<TD>
 <A HREF="https://www.raspberrypi.com/news/trixie-the-new-version-of-raspberry-pi-os/">Trixie OS</A> &amp;
 <A HREF="https://www.python.org/">Python</A> 
</TD>
<TD> 
 <A HREF="https://www.adafruit.com/product/6408">RPi Touch Display 2 - 5" 720x1280</A> 
</TD> 
<TD>
 <A HREF="https://www.adafruit.com/product/5188">DS3231</A>
</TD>
<TD>
 <A HREF="https://www.adafruit.com/product/4494">DPS310</A> 
</TD> 
</TR>

</TABLE>

<HR>

## Kite Altimeter Hardware Version 7

</P> 
<p align="center"> <img width="723" height="530" src="/Images/V7back2.png">
</p>

Raspberry Pi 5 with cooling fan mounted to the back side of the 5" touch display 2. Long I2C four wire cable (red, black, yellow and blue) from the I2C port of the GPIO connector to the DPS310 pressure sensor. Short I2C cable from the DPS310 to the RTC.

Clear plastic from food containers mounted on four standoffs to protect the back of the Raspberry Pi 5 and to hold the DPS310 and RTC boards.

</P> 
<p align="center"> <img width="803" height="730" src="/Images/V7bottom2.png">
</p>

</P> 
<p align="center"> <img width="567" height="433" src="/Images/V7left2.png">
</p>

</P> 
<p align="center"> <img width="624" height="423" src="/Images/V7right3.png">
</p>


# DPS310 Pressure Logger – Pressure V7.4

</P> 
<p align="center"> <img width="720" height="1280" src="/Images/V7_4Screen3.png">
</p>

Raspberry Pi <A HREF="https://www.raspberrypi.com/news/trixie-the-new-version-of-raspberry-pi-os/">Trixie OS</A> running
<A HREF="https://www.python.org/">Python 3.13.5</A> reading pressure and temperature from DPS310 sensor. 

This project runs on a Raspberry Pi and reads barometric pressure and temperature from a DPS310 sensor. It provides:

- A live GUI window (`Pressure V7.4`) with current values, trends, noise estimates, and history plots
- Continuous CSV logging with timestamped data for offline analysis

The GUI and logger are designed for atmospheric work such as kite altimeters, weather watching, and pressure stability studies.


---

## Live GUI Display

The GUI window shows real-time pressure and temperature data, with basic analytics. 
Each line/plot in the window is described below.

### Pressure (hPa)
**Example:** `971.726`

This is the most recent raw barometric pressure reading from the DPS310 sensor in hectopascals (hPa). 
1 hPa = 100 pascals ≈ 0.02953 inHg.

This value updates continuously (about once per second in this version).

---

### Smoothed (hPa)
**Example:** `971.768`

This is a short-term moving average of pressure. 
Purpose:
- Reduces short-term sensor noise
- Makes trends easier to see
- Gives a better "steady" atmospheric pressure number than the instantaneous reading

In V7.4, the smoothing window is ~30 seconds of recent data.

---

### Trend (hPa/min)
**Example:** `-0.061`

This is the rate of change of pressure, in hectopascals per minute.

How to interpret:
- Negative value (e.g. `-0.061`) → pressure is dropping
- Positive value → pressure is rising
- Near zero → stable

Why it matters:
- Falling pressure can indicate changing weather
- In a kite application, rapid changes can indicate altitude changes or gust loading

In this version, the trend is calculated over approximately one minute of recent data.

---

### Noise (hPa RMS)
**Example:** `0.026`

This is the short-term RMS (root mean square) noise level of the pressure signal, in hPa.

What it tells you:
- Lower RMS → very stable readings
- Higher RMS → turbulence, vibration, or electrical noise

In V7.4, the RMS is computed over about the last 30 seconds of samples.

---

### Mini History Plots (Sparklines)

The GUI includes four small strip charts that show how pressure has changed over different time spans. 
Each chart is labeled with its time window:

1. **Last 60s (hPa)** 
 Shows fine-grain behavior: small dips, spikes, gust effects.

2. **Last 600s (hPa)** 
 ~10 minutes of history. Helps show short patterns (for example, oscillations or repeated bumps).

3. **Last 1 hr (hPa)** 
 Tracks medium-term trends. You can see slow climbs/drops.

4. **Last 12 hr (hPa)** 
 Long-term pressure evolution across half a day. Great for weather trend / frontal passage.

All plots are drawn in hPa vs. time (older data on the left, newest on the right). 
These are not interactive; they’re intended for at-a-glance situational awareness.

---

### Pressure (inHg)
**Example:** `28.695`

Same pressure as above, converted to inches of mercury (inHg). 
This is the traditional U.S. weather station / altimeter setting unit.

Conversion is performed in software from the hPa reading.

---

### Temperature (°C) and Temperature (°F)
**Examples:** 
- `23.46 °C` 
- `74.23 °F`

This is the DPS310 internal temperature sensor reading, displayed in both Celsius and Fahrenheit.

Note:
- This is sensor temperature, not calibrated ambient air temperature.
- The value can read higher than room air if the sensor is near warm electronics.

---

### Timestamp (UTC)
**Example:** 
`2025-10-26T17:13:55.547080+00:00`

All samples in the GUI and in the CSV logs are tagged with a UTC timestamp in ISO 8601 format.

Format: 
`YYYY-MM-DDThh:mm:ss.ssssss+00:00` 
Example: `2025-10-26T17:13:55.547080+00:00`

Using UTC makes it easier to analyze data captured in different locations or time zones.


---

## CSV Logging

In addition to the GUI, the program continuously writes data to a `.CSV` file for later analysis.

A header (commented with `#`) explains each column:

```text
# timestamp_iso8601_utc : UTC time of sample (ISO 8601)
# temp_C : Sensor temperature in degrees C
# temp_F : Sensor temperature in degrees F
# pressure_hPa : Raw pressure in hPa from DPS310
# pressure_inHg : Pressure converted to inches of mercury
# smooth_hPa_30s_avg : Moving-average pressure over last ~30s
# trend_hPa_per_min : Pressure change rate (hPa/min) over ~1 min
# noise_hPa_RMS_30s : RMS noise (std dev) of pressure over last ~30s
#
# Columns (in order):
# timestamp_iso8601_utc,temp_C,temp_F,pressure_hPa,pressure_inHg,smooth_hPa_30s_avg,trend_hPa_per_min,noise_hPa_RMS_30s
2025-10-26T01:22:07.871332+00:00,26.067,78.920,963.891,28.4637,963.891,0.000,0.000
2025-10-26T01:22:08.878870+00:00,26.056,78.900,963.895,28.4638,963.893,0.257,0.002
2025-10-26T01:22:09.876598+00:00,26.046,78.882,963.893,28.4637,963.893,0.059,0.002
..
```

<HR>

# GPS/GNSS 
## HiLetgo VK172 G-Mouse USB GPS/GLONASS USB GPS Receiver

</P> 
<p align="center"> <img width="398" height="593" src="/Images/GPSfront.png">
</p>

</P> 
<p align="center"> <img width="439" height="638" src="/Images/GPSback.png">
</p>

+ [Website](https://device.report/hiletgo/13?__cf_chl_tk=Q110bP5iebU7exOEHx.VMGX7Aw7XaV0okPRcmaLsQDI-1761693090-1.0.1.1-zalz_hztDIkYTnyM3bEF44m9lFVlM9H81KbF3j9nVHw)
+ [Amazon](https://www.amazon.com/dp/B01MTU9KTF/?coliid=I1ILW02DCZJ03E&colid=XSJ6DS90PQ0Q&ref_=list_c_wl_lv_ov_lig_dp_it_im&th=1)




<HR>

# Version 7 Development Sytem 

</P> 
<p align="center"> <img width="780" height="439" src="/Images/V7dev.png">
</p>

+ Raspberry Pi 5 with the 5" touch display 2.
+ Raspberry Pi power supply
+ Two 1080 HDMI monitors
+ USB C power supply for HDMI monitors
+ Wireless mouse and keyboard
+ USB 3 hub
+ Micro SD card reader
+ 128 GB SD card for backups
+ USB GPS
+ Blue Tooth speaker

<HR>

# DPS310 Pressure Acquisition and Logging: Raspberry Pi 5 vs RP2040 Comparison

This document compares the use of a **Raspberry Pi 5 with Touch Display** and an **RP2040 microcontroller** (e.g., Adafruit Feather RP2040, Raspberry Pi Pico) for **pressure measurement, data logging, and analysis** using the **Adafruit DPS310 barometric pressure sensor**.

---

## 🧩 System Overview

| Feature | Raspberry Pi 5 + Touch Display | RP2040 Microcontroller |
|----------|-------------------------------|------------------------|
| **Processor** | 2.4 GHz quad-core Cortex-A76 (64-bit) | Dual-core Cortex-M0+ @ 133 MHz |
| **Operating System** | Raspberry Pi OS (Linux desktop) | No OS / CircuitPython or MicroPython |
| **Power Usage** | 5 V @ 2–3 A | 5 V @ 0.1–0.3 A |
| **Storage** | microSD card (32 GB or more) | Flash (2–16 MB) + optional SD |
| **Display Interface** | Built-in HDMI / DSI Touch Display | Optional OLED / E-Ink / Serial terminal |
| **I/O Interfaces** | USB, I²C, SPI, UART, GPIO (3.3 V logic) | I²C, SPI, UART, GPIO (3.3 V logic) |
| **Programming Languages** | Python 3, C/C++, Matplotlib, Pandas | CircuitPython, MicroPython, C/C++ |
| **Typical Application** | Real-time display and data analysis | Edge data collection and logging |

---

## 📊 DPS310 Pressure Acquisition and Data Logging

### Raspberry Pi 5 Advantages

✅ **High-speed data processing** 
 • Capable of fast sampling (> 50 Hz) and real-time graphing with Matplotlib. 

✅ **Integrated display and GUI control** 
 • Supports full Tkinter / Qt / GTK interfaces for interactive data visualization. 

✅ **Large storage and analysis capability** 
 • Easily logs to CSV or SQLite databases for extended sessions. 

✅ **Advanced analysis tools available** 
 • Numpy, Pandas, Scipy enable trend analysis, moving-average, and variance computation in real time. 

✅ **Convenient network connectivity** 
 • Wi-Fi and Ethernet allow remote data upload and SSH access. 

---

### Raspberry Pi 5 Disadvantages

❌ **Higher power consumption** 
 • Requires stable 5 V 3 A supply—less suitable for battery operation. 

❌ **Longer boot time** 
 • Full Linux boot (~30 seconds) before data acquisition can begin. 

❌ **Less rugged for field use** 
 • microSD cards and connectors can be vulnerable to vibration or moisture. 

❌ **Complex software stack** 
 • Requires OS updates, package dependencies, and possible I²C permission setup. 

---

### RP2040 Advantages

✅ **Low power and instant-on** 
 • Starts logging within milliseconds—ideal for battery or kite-borne operation. 

✅ **Compact and lightweight** 
 • Small form factor and minimal support components for embedded use. 

✅ **Simpler software environment** 
 • Runs directly from flash memory with CircuitPython or MicroPython—no OS maintenance. 

✅ **Deterministic timing** 
 • Excellent for precise sampling and time-synchronized sensor reads. 

✅ **Low cost** 
 • RP2040 boards are typically under $10 USD. 

---

### RP2040 Disadvantages

❌ **Limited processing and RAM** 
 • Cannot run advanced data analysis or graphing libraries locally. 

❌ **No native display GUI** 
 • Requires external display or PC connection for visualization. 

❌ **Limited storage** 
 • On-board flash is small; SD card logging needs additional hardware. 

❌ **No multi-threaded OS** 
 • Data logging and communication tasks must be manually coordinated. 

---

## 🧠 Recommended Use Cases

| Application | Best Platform | Notes |
|--------------|---------------|-------|
| **Bench-top testing / live analysis** | Raspberry Pi 5 + Touch Display | GUI graphs, Python data analysis tools. |
| **Field logging / kite flight instrumentation** | RP2040 microcontroller | Low power, lightweight, rugged design. |
| **Remote monitoring with network upload** | Raspberry Pi 5 (headless mode) | Use SSH or web dashboard for real-time monitoring. |
| **Battery-powered sensor node** | RP2040 | Run from Li-ion or Li-Po cells for hours or days. |

---

## ⚙️ Example DPS310 Integration

### Raspberry Pi 5 Example (Python 3)

```python
import time, board, adafruit_dps310

i2c = board.I2C()
sensor = adafruit_dps310.DPS310(i2c)

while True:
 print(f"{sensor.pressure:.2f} hPa {sensor.temperature:.2f} °C")
 time.sleep(1)
```
### RP2040 Example (CircuitPython)

```python
import time, board, adafruit_dps310

i2c = board.I2C()
sensor = adafruit_dps310.DPS310(i2c)

while True:
 print((sensor.pressure, sensor.temperature))
 time.sleep(1)
```
## 📈 Summary Comparison

| **Category** | **Raspberry Pi 5 + Touch Display** | **RP2040 Microcontroller** |
|---------------|------------------------------------|-----------------------------|
| **Power Usage** | High (≈10× RP2040) | Very Low |
| **Boot Time** | ~30 seconds | < 1 second |
| **GUI Support** | Full desktop GUI (Tkinter, Qt, GTK) | Minimal (OLED / serial text) |
| **Storage Capacity** | Large (microSD 32 GB+) | Limited (Flash 2–16 MB or SD card) |
| **Code Complexity** | High (Linux, packages, permissions) | Low (CircuitPython / MicroPython) |
| **Data Analysis Tools** | Built-in (NumPy, Pandas, Matplotlib) | External (requires PC) |
| **Connectivity** | Wi-Fi, Ethernet, USB | UART, I²C, SPI, LoRa, Bluetooth (add-on) |
| **Portability** | Desktop or bench use | Excellent for field use |
| **Cost** | High (~$100+ with display) | Low (~$10–$20 board only) |

---

## 🧭 Conclusion

Both platforms can successfully acquire and log pressure data using the **Adafruit DPS310**, but their **optimal roles differ**:

- 🖥️ **Raspberry Pi 5 + Touch Display** 
 Ideal for **real-time visualization**, **interactive GUI control**, and **in-depth data analysis** using full Python libraries. 
 Best suited for **laboratory testing**, **bench experiments**, and **development environments**.

- ⚙️ **RP2040 Microcontroller** 
 Optimized for **low-power, lightweight, and portable** field applications such as **kite-borne data logging** or **edge sensing**. 
 Offers deterministic timing, instant startup, and long battery life, making it excellent for autonomous deployments.

> 💡 **Recommended Workflow:** 
> Use the **RP2040** to collect data in the field, then transfer the logged CSV files to the **Raspberry Pi 5** for graphical analysis, filtering, and trend evaluation.

---

**Author:** David Haworth (WA9ONY) 
**Date:** October 2025 
**License:** MIT 
**Keywords:** DPS310, Raspberry Pi 5, RP2040, Pressure Sensor, Data Logging, Kite Instrumentation


<HR>
