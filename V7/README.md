<P align="center"> - <A HREF="https://www.qrz.com/db/WA9ONY">WA9ONY</A> - <A HREF="https://www.youtube.com/@Kites-Flying">YouTube Kites-Flying</A> - <A HREF="https://www.youtube.com/user/DavidAHaworth">YouTube David Haworth</A> - <A HREF="http://www.stargazing.net/david/index.html">Website</A> -
</P> 

<p align="center"> <img width="333" height="591" src="/Images/GPSporch.png">
</p>

Raspberry Pi 5 with the 5" touch display 2 connected to 
+ INIU USB 10ah battery bank behind the Raspberry Pi 5.
+ HiLetgo VK172 G-Mouse USB GPS/GLONASS USB GPS Receiver on the top of the sticks.
+ Pink 3' USB A extension cable between the Raspberry Pi 5 and the GPS/GLONASS USB.

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
<HR>

# Kite Altimeter Hardware Version 7

<p align="center"> <img width="588" height="588" src="/Images/V7top.JPEG">
</p>

Raspberry Pi 5 with the 5" touch display 2 connected to INIU USB 10ah battery bank.

<p align="center"> <img width="723" height="530" src="/Images/V7back2.png">
</p>

Raspberry Pi 5 with cooling fan mounted to the back side of the 5" touch display 2. Long I2C four wire cable (red, black, yellow and blue) from the I2C port of the GPIO connector to the DPS310 pressure sensor. Short I2C cable from the DPS310 to the RTC.

Clear plastic from food containers mounted on four standoffs to protect the back of the Raspberry Pi 5 and to hold the DPS310 and RTC boards.
 
<p align="center"> <img width="803" height="730" src="/Images/V7bottom2.png">
</p>
 
<p align="center"> <img width="567" height="433" src="/Images/V7left2.png">
</p>
 
<p align="center"> <img width="700" height="1200" src="/Images/V7right3.png">
</p>

<HR>
<HR>

# DPS310 Pressure Logger – Pressure V7.4
 
<p align="center"> <img width="720" height="1280" src="/Images/V7screen4.png">
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
<HR>

# HiLetgo VK172 G-Mouse USB GPS/GLONASS USB GPS Receiver

<p><img width="398" height="593" src="/Images/GPSfront.png"> <img width="439" height="638" src="/Images/GPSback.png">
</p>

+ [Website](https://device.report/hiletgo/13?__cf_chl_tk=Q110bP5iebU7exOEHx.VMGX7Aw7XaV0okPRcmaLsQDI-1761693090-1.0.1.1-zalz_hztDIkYTnyM3bEF44m9lFVlM9H81KbF3j9nVHw)
+ [Amazon](https://www.amazon.com/dp/B01MTU9KTF/?coliid=I1ILW02DCZJ03E&colid=XSJ6DS90PQ0Q&ref_=list_c_wl_lv_ov_lig_dp_it_im&th=1)

YouTube
+ [$12.00 Glonass GPS USB/U-blox7 For  GTAC Toughpad F110. Time Sync For FT8 #WSJTX #JS8CALL For SOTA!](https://youtube.com/shorts/U0byJIMqPi0?si=3vLSeFUYgbZuL1PO)


## GPS/GLONASS USB Plug In and Identify

Run these commands in a terminal:

lsusb
```text
david@raspberrypi:~ $ lsusb
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 002: ID 046d:c534 Logitech, Inc. Nano Receiver
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
david@raspberrypi:~ $ lsusb
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 002: ID 046d:c534 Logitech, Inc. Nano Receiver
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Device 002: ID 1546:01a7 U-Blox AG [u-blox 7]
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
david@raspberrypi:~ $ 
```

USB GPS found
```text
Bus 003 Device 002: ID 1546:01a7 U-Blox AG [u-blox 7]
```

dmesg --follow

```text
david@raspberrypi:~ $ dmesg --follow

[235020.220809] usb 3-1: new full-speed USB device number 2 using xhci-hcd
[235020.373242] usb 3-1: New USB device found, idVendor=1546, idProduct=01a7, bcdDevice= 1.00
[235020.373250] usb 3-1: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[235020.373253] usb 3-1: Product: u-blox 7 - GPS/GNSS Receiver
[235020.373255] usb 3-1: Manufacturer: u-blox AG - www.u-blox.com
[235020.565400] cdc_acm 3-1:1.0: ttyACM0: USB ACM device
[235020.565433] usbcore: registered new interface driver cdc_acm
[235020.565435] cdc_acm: USB Abstract Control Model driver for USB modems and ISDN adapters

```

Then unplug and re-plug the dongle.
Look for something like:

[ 1234.567890] usb 1-1.2: new full-speed USB device number 8 using xhci_hcd
[ 1234.678901] cdc_acm 1-1.2:1.0: ttyACM0: USB ACM device

or:

[ 1234.678901] cp210x converter now attached to ttyUSB0

```text
david@raspberrypi:~ $ dmesg --follow

[235020.220809] usb 3-1: new full-speed USB device number 2 using xhci-hcd
[235020.373242] usb 3-1: New USB device found, idVendor=1546, idProduct=01a7, bcdDevice= 1.00
[235020.373250] usb 3-1: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[235020.373253] usb 3-1: Product: u-blox 7 - GPS/GNSS Receiver
[235020.373255] usb 3-1: Manufacturer: u-blox AG - www.u-blox.com
[235020.565400] cdc_acm 3-1:1.0: ttyACM0: USB ACM device
[235020.565433] usbcore: registered new interface driver cdc_acm
[235020.565435] cdc_acm: USB Abstract Control Model driver for USB modems and ISDN adapters
[235807.839382] usb 3-1: USB disconnect, device number 2
[235819.863802] usb 3-1: new full-speed USB device number 3 using xhci-hcd
[235820.015952] usb 3-1: New USB device found, idVendor=1546, idProduct=01a7, bcdDevice= 1.00
[235820.015959] usb 3-1: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[235820.015962] usb 3-1: Product: u-blox 7 - GPS/GNSS Receiver
[235820.015964] usb 3-1: Manufacturer: u-blox AG - www.u-blox.com
[235820.207020] cdc_acm 3-1:1.0: ttyACM0: USB ACM device
^C
david@raspberrypi:~ $ 
```

That line tells us which serial device to use — /dev/ttyACM0 or /dev/ttyUSB0.

```text
[235820.207020] cdc_acm 3-1:1.0: ttyACM0: USB ACM device
```

[dmesg log](dmesg.txt)

## View Raw NMEA Data

Install tools (if not already):

sudo apt update
sudo apt install -y gpsd gpsd-clients minicom


Then run (substitute your device path):

sudo minicom -b 9600 -D /dev/ttyACM0

You should see live sentences like:

$GPGGA,202532.00,4542.1342,N,12243.9456,W,1,08,0.95,74.3,M,-17.2,M,,*65
$GPRMC,202532.00,A,4542.1342,N,12243.9456,W,0.022,,281023,,,A*7C

Those are NMEA 0183 messages — proof it’s alive.

If the output is gibberish, exit (Ctrl-A, then Q) and try 38400 or 115200 baud.

```text
[2025-10-29 12:01:32] $GPGLL,,,,,,V,N*64
[2025-10-29 12:01:33] $GPRMC,,V,,,,,,,,,,N*53
[2025-10-29 12:01:33] $GPVTG,,,,,,,,,N*30
[2025-10-29 12:01:33] $GPGGA,,,,,,0,00,99.99,,,,,,*48
[2025-10-29 12:01:33] $GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
[2025-10-29 12:01:33] $GPGSV,6,1,22,04,,,22,05,,,23,06,,,23,07,,,23*7F
[2025-10-29 12:01:33] $GPGSV,6,2,22,08,,,14,09,,,22,10,,,22,11,,,22*78
[2025-10-29 12:01:33] $GPGSV,6,3,22,12,,,23,13,,,22,14,,,22,15,,,22*7D
[2025-10-29 12:01:33] $GPGSV,6,4,22,16,,,23,17,,,22,20,,,25,22,,,22*7E
[2025-10-29 12:01:33] $GPGSV,6,5,22,23,,,23,24,,,22,27,,,23,29,,,23*72
[2025-10-29 12:01:33] $GPGSV,6,6,22,30,,,22,32,,,22*7B
[2025-10-29 12:01:33] $GPGLL,,,,,,V,N*64
[2025-10-29 12:01:34] $GPRMC,,V,,,,,,,,,,N*53
[2025-10-29 12:01:34] $GPVTG,,,,,,,,,N*30
[2025-10-29 12:01:34] $GPGGA,,,,,,0,00,99.99,,,,,,*48
[2025-10-29 12:01:34] $GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
[2025-10-29 12:01:34] $GPGSV,6,1,22,04,,,20,05,,,20,06,,,20,07,,,21*7F
[2025-10-29 12:01:34] $GPGSV,6,2,22,08,,,10,09,,,21,10,,,21,11,,,18*75
[2025-10-29 12:01:34] $GPGSV,6,3,22,12,,,20,13,,,21,14,,,21,15,,,21*7D
[2025-10-29 12:01:34] $GPGSV,6,4,22,16,,,20,17,,,19,20,,,21,22,,,20*73
[2025-10-29 12:01:34] $GPGSV,6,5,22,23,,,21,24,,,20,27,,,20,29,,,21*73
[2025-10-29 12:01:34] $GPGSV,6,6,22,30,,,21,32,,,19*70
[2025-10-29 12:01:34] $GPGLL,,,,,,V,N*64
[2025-10-29 12:01:35] $GPRMC,,V,,,,,,,,,,N*53
[2025-10-29 12:01:35] $GPVTG,,,,,,,,,N*30
[2025-10-29 12:01:35] $GPGGA,,,,,,0,00,99.99,,,,,,*48
[2025-10-29 12:01:35] $GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
[2025-10-29 12:01:35] $GPGSV,5,1,19,04,,,19,05,,,18,06,,,26,08,,,13*7D
[2025-10-29 12:01:35] $GPGSV,5,2,19,09,,,19,10,,,21,12,,,18,13,,,21*7E
[2025-10-29 12:01:35] $GPGSV,5,3,19,15,,,19,16,,,18,17,,,17,20,,,21*74
[2025-10-29 12:01:35] $GPGSV,5,4,19,22,,,19,23,,,22,24,,,18,27,,,18*7A
[2025-10-29 12:01:35] $GPGSV,5,5,19,29,,,22,30,,,22,32,,,17*7E
[2025-10-29 12:01:35] $GPGLL,,,,,,V,N*64
```

[minicom log](minicomlog.txt)
 
<p align="center"> <img width="848" height="744" src="/Images/minicomHelp.png">
</p>

# gpsd and cgps Overview

This section explains how **gpsd** (the GPS Daemon) and **cgps** (its command-line client) work together under Linux to provide GPS/GNSS position, velocity, and timing data.

---

## What is gpsd?

### **Overview**
`gpsd` is a **background service (daemon)** that interfaces with GPS and GNSS receivers. It reads, parses, and distributes positioning data to multiple applications in a standardized way.

It acts as a **data broker** between GPS hardware and client software.

### **Key Functions**
| Function | Description |
|-----------|--------------|
| **Device Management** | Automatically detects GPS devices on USB, serial, or TCP interfaces. |
| **Protocol Parsing** | Supports NMEA 0183, SiRF, UBX, AIS, and other binary protocols. |
| **Data Normalization** | Converts raw sentences into a consistent, JSON-formatted data stream. |
| **Network Service** | Provides access through TCP port **2947** so clients can connect remotely or locally. |
| **Multi-client Capability** | Supports multiple programs at the same time (e.g., `cgps`, `xgps`, Python scripts). |

### **Typical Startup Commands**
```bash
sudo systemctl start gpsd
sudo systemctl enable gpsd
```
After launching, gpsd listens on port **2947**, ready to serve data to any compatible client.

---

## cgps

### **Overview**
`cgps` is a **text-based client** for gpsd. It connects to the gpsd service and displays live data from the GPS receiver in a structured, easy-to-read terminal interface.

### **Key Features**
| Feature | Description |
|----------|--------------|
| **Real-Time Data Display** | Shows position, speed, altitude, and time updates every second. |
| **Fix Mode Reporting** | Displays NO FIX, 2D FIX, 3D FIX, or DGPS FIX depending on signal quality. |
| **Error Metrics (DOP)** | Reports dilution-of-precision values: HDOP, VDOP, PDOP, TDOP, and GDOP. |
| **ECEF Data** | Displays Cartesian coordinates (X, Y, Z) in Earth-Centered, Earth-Fixed format. |
| **Satellite Table** | Lists all visible satellites with azimuth, elevation, signal strength (SNR), and usage in fix. |

### **Example Command**
```bash
cgps -s
```
The `-s` option enables a simplified terminal display that updates in real time.

---

## How They Work Together

```
┌───────────────────────────────────────────────────────────┐
│                 GNSS SATELLITE CONSTELLATIONS             │
│  (GPS, GLONASS, Galileo, BeiDou, SBAS, QZSS)             │
└──────────────┬────────────────────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────────────────────┐
│               GPS RECEIVER / DONGLE (e.g., USB)           │
│   Sends NMEA/UBX messages via /dev/ttyUSB0 or similar     │
└──────────────┬────────────────────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────────────────────┐
│                    gpsd (GPS Daemon)                      │
│  Parses NMEA data, manages devices, serves TCP :2947      │
│  Converts to JSON data for clients                        │
└──────────────┬────────────────────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────────────────────┐
│                     cgps (Client App)                     │
│  Connects to gpsd → Displays:                             │
│   - Time, Lat, Lon, Alt                                   │
│   - Speed, Track, Climb                                   │
│   - Fix Mode & DOP                                        │
│   - Satellite Table                                       │
└───────────────────────────────────────────────────────────┘
```

---

## Analogy

| Component | Analogy |
|------------|----------|
| **GPS Receiver** | The aircraft sending its position data. |
| **gpsd** | The control tower organizing and translating the signals. |
| **cgps** | The radar screen showing what the tower reports. |

---

## Communication Flow Example

1. The GPS receiver sends raw NMEA sentences like:
   ```
   $GPGGA,212856.00,4534.1234,N,12222.5678,W,1,10,0.8,113.4,M,-17.0,M,,*5A
   ```
2. `gpsd` reads and parses this data.
3. The parsed JSON data becomes available to clients on TCP port 2947:
   ```json
   {"class":"TPV","lat":45.56872,"lon":-122.37563,"alt":342.1,"speed":0.03}
   ```
4. `cgps` subscribes to gpsd and displays this information in human-readable form.

---

## Summary

- **gpsd**: The backend daemon that reads and standardizes GPS/GNSS data.
- **cgps**: A client program that queries gpsd and presents data to the user.
- Together, they form a modular and flexible GPS architecture for Linux systems.

These tools are invaluable for:
- Testing GPS receivers.
- Logging real-time GNSS data.
- Building embedded systems (like Raspberry Pi or Arduino-based navigation and data-logging projects).

---

## References
- [gpsd Project Documentation](https://gpsd.gitlab.io/gpsd/)
- [cgps Man Page](https://linux.die.net/man/1/cgps)
- [gpspipe Tool](https://gpsd.gitlab.io/gpsd/gpspipe.html)
- [NMEA 0183 Reference](https://gpsd.gitlab.io/gpsd/NMEA.html)

---

### GPS/GLONASS USB Test with gpsd and cgps

Stop any background gpsd service (to avoid conflicts):

sudo systemctl stop gpsd.socket
sudo systemctl stop gpsd

```text
david@raspberrypi:~ $ sudo systemctl stop gpsd.socket sudo systemctl stop gpsd
Failed to stop systemctl.service: Unit systemctl.service not loaded.
Failed to stop stop.service: Unit stop.service not loaded.
david@raspberrypi:~ $ 
```

Then launch manually:

sudo gpsd -N -n /dev/ttyACM0 -F /var/run/gpsd.sock


In another terminal:

cgps -s


You’ll see a live terminal dashboard: latitude, longitude, altitude, time, fix type, satellites tracked, etc.

If that works, your VK172 is fully functional.

<HR>
<HR>

</P> 
<p align="center"> <img width="602" height="621" src="/Images/cgpsAnalysis.png">
</p>

# cgps Linux CLI Display Reference

This section describes every field and value shown in the Linux command-line utility **`cgps`**, which displays real-time data from a GPS receiver via **gpsd** in the above image from the Raspberry Pi 5 touch display out side on the porch.

---

## Display Layout Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ TIME & FIX INFO                                                              │
│ Time: 2025-10-29T21:37:19.000Z (18 satellites)                               │
│ Status: 3D DGPS FIX (1195 secs)                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ POSITION                                                                     │
│ Latitude: 45.66849659 N     Longitude: 122.38632525 W                        │
│ Altitude: HAE 1062.997 ft   MSL 1134.970 ft                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ MOTION & ORIENTATION                                                         │
│ Speed: 0.07 mph   Track (True/Var): 285.5° / 15.0°   Climb: 3.94 ft/min      │
├──────────────────────────────────────────────────────────────────────────────┤
│ POSITION ERRORS & DOP VALUES                                                 │
│ XDOP(EPX)=2.89  YDOP(EPY)=2.53  VDOP(EPV)=1.84  HDOP(CEP)=0.86               │
│ PDOP(SEP)=2.03  TDOP=1.12  GDOP=2.32                                         │
│ Position Error: ±31–35 ft  Speed Err: ±48 mph                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ SYSTEM TIME & REFERENCE INFO                                                 │
│ Time Offset: 0.092943 s  Grid: CN85tq30                                      │
│ ECEF (X,Y,Z): (-7,846,307, -12,370,327, 14,894,381) ft                       │
│ ECEF Vel (ft/s): (-0.098, +0.033, +0.066)                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ SATELLITES USED (right column)                                               │
│ GP: 4,7,9,10,13,16,20,21,27,30                                               │
│ SBAS: 133,138  QZSS: 1,3                                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Time Information

- **Time:** The current UTC (Coordinated Universal Time) from the GPS satellite system. Example: `2025-10-29T21:37:19.000Z`.
- **(18):** Number of satellites currently used to compute the position fix.

---

## Position

- **Latitude / Longitude:** Geographic coordinates in decimal degrees.
  - Example: `45.66849659 N`, `122.38632525 W`
- **Alt (HAE, MSL):** Two altitude references:
  - **HAE (Height Above Ellipsoid):** Height above the WGS-84 reference ellipsoid.
  - **MSL (Mean Sea Level):** Height above mean sea level (includes geoid correction).
  - Example: `1062.997 ft (HAE)`, `1134.970 ft (MSL)`

---

## Motion and Direction

- **Speed:** Current horizontal velocity (mph, knots, or m/s depending on configuration).
  - Example: `0.07 mph`
- **Track (true, var):** Heading direction relative to:
  - **True North** (e.g., `285.5°`)
  - **Magnetic variation** (difference between true and magnetic north, e.g., `15.0°`)
- **Climb:** Vertical velocity in feet per minute (ft/min). Example: `3.94 ft/min`

---

## Fix Status

- **Status:** Type of GPS fix and correction status.
  - `NO FIX`: No satellite lock.
  - `2D FIX`: Latitude and longitude only.
  - `3D FIX`: Includes altitude.
  - `3D DGPS FIX`: Differential GPS correction applied.
- **(1195 secs):** Duration (in seconds) since DGPS correction started.

---

## Position Accuracy (Dilution of Precision)

Each DOP (Dilution of Precision) describes the error amplification due to satellite geometry.

| Label | Description | Units | Example |
|-------|--------------|--------|----------|
| **XDOP (EPX)** | Longitude error | ft | ±35.5 |
| **YDOP (EPY)** | Latitude error | ft | ±31.2 |
| **VDOP (EPV)** | Altitude error | ft | ±34.7 |
| **HDOP (CEP)** | Horizontal dilution / Circular error probable | ft | ±13.4 |
| **PDOP (SEP)** | 3D position dilution | ft | ±31.6 |
| **TDOP** | Time dilution of precision | — | 1.12 |
| **GDOP** | Geometric DOP (overall position and time) | — | 2.32 |
| **EPS** | Speed error | mph | ±48.4 |
| **EPD** | Track error | mph | — |

---

## Time and Synchronization

- **Time offset:** GPS receiver time offset from system clock, in seconds.
  - Example: `0.092943125 s`
- **Grid Square:** Maidenhead grid locator used in amateur radio (e.g., `CN85tq30`).

---

## ECEF (Earth-Centered, Earth-Fixed) Coordinates

ECEF coordinates describe the GPS position in a 3D Cartesian reference frame centered at Earth’s center.

| Axis | Meaning | Example Value | Velocity |
|------|----------|----------------|-----------|
| **X** | Earth center → intersection of Equator and Prime Meridian | -7,846,307.606 ft | -0.098 ft/s |
| **Y** | 90° east longitude direction | -12,370,327.358 ft | +0.033 ft/s |
| **Z** | Earth’s rotation axis (northward) | +14,894,381.380 ft | +0.066 ft/s |

---

## GNSS Satellites Used

Right-side column shows the satellites currently tracked:

| System | Label Prefix | Example IDs |
|---------|--------------|--------------|
| GPS | `GP` | 4, 7, 9, 10, 13, 16, 20, 21, 27, 30 |
| SBAS (WAAS, EGNOS, etc.) | `SB` | 133, 138 |
| QZSS (Japan) | `QZ` | 1, 3 |
| GLONASS | `GL` | — (none listed) |
| Galileo | `GA` | — (none listed) |

Numbers represent individual satellite PRNs (Pseudo-Random Noise IDs).

---

## Summary

This `cgps` display provides real-time diagnostic insight into a GPS receiver’s:

- Geographic position (lat, lon, altitude)
- Motion (speed, climb, heading)
- Satellite status and number of signals used
- Positional accuracy (DOP values)
- Time synchronization and ECEF coordinates

This information is crucial for debugging GPS hardware, validating data quality, and ensuring stable satellite locks in applications like drones, kites, vehicles, or sensor networks.

---

## References

- [gpsd Project Documentation](https://gpsd.gitlab.io/gpsd/)
- [cgps Man Page](https://linux.die.net/man/1/cgps)
- [NMEA 0183 Standard Sentences](https://gpsd.gitlab.io/gpsd/NMEA.html)

---

<HR>
<HR>

<p align="center"> <img width="647" height="651" src="/Images/cgpsSats2.png">
</p>

# cgps Satellite Information Display Reference

This document describes each field displayed in the **satellite view panel** of the Linux command-line utility **`cgps`**, which reports the status and signal information for satellites being tracked by a GPS receiver through **gpsd**.

---

## Overview

The satellite table provides details about each satellite signal currently being **seen** by the receiver and whether it is **used** in the current position fix.

The top header line displays summary counts:

```
Seen 17 / Used 11
```

- **Seen 17:** Total number of satellites detected (in view of the receiver).
- **Used 11:** Number of satellites actively used in the 3D fix computation.

---

## Table Columns Explained

| Column | Description | Example | Units / Notes |
|:--------|:-------------|:---------|:----------------|
| **GNSS** | The Global Navigation Satellite System used. Common identifiers:  | | |
| | `GP` = GPS (United States) | `GP` |  |
| | `GL` = GLONASS (Russia) | — | — |
| | `GA` = Galileo (Europe) | — | — |
| | `SB` = SBAS (WAAS/EGNOS/MSAS/GAGAN) | `SB133` | — |
| | `QZ` = QZSS (Japan) | `QZ1`, `QZ4` | — |
| **S** | Satellite number within the system (Space Vehicle ID). | `4`, `7`, `30` | Integer |
| **PRN** | Pseudo-Random Noise (PRN) code identifier for that satellite. This number identifies each satellite’s broadcast signal. | `4`, `7`, `30`, `46`, `51`, `194` | Integer |
| **Elev (°)** | Elevation angle of the satellite above the horizon. Higher values mean the satellite is more directly overhead and typically has a stronger, more stable signal. | `29.0`, `70.0`, `23.0` | Degrees |
| **Azim (°)** | Azimuth — direction of the satellite from true north, measured clockwise. | `130.0`, `294.0`, `46.0` | Degrees |
| **SNR (dB)** | Signal-to-Noise Ratio — a measure of signal quality and strength. | `36.0`, `31.0`, `27.0` | Decibels (dB-Hz) |
| **Use** | Indicates whether the satellite is being used in the position fix calculation. | `Y` = Used, `N` = Not used | Boolean |

---

## Example Data Interpretation

```
GP   4   4   29.0   130.0   36.0   Y
```

This means:
- **GNSS:** GPS system (USA)
- **Satellite ID:** 4 (PRN 4)
- **Elevation:** 29° above horizon
- **Azimuth:** 130° (southeast)
- **Signal Strength:** 36 dB (good)
- **Used in fix:** Yes (contributing to position)

---

## GNSS Constellation Types

| System | Abbrev. | Region | Frequency Bands | Notes |
|:--------|:---------|:--------|:----------------|:-------|
| **GPS** | GP | USA | L1, L2, L5 | Primary GNSS in North America |
| **GLONASS** | GL | Russia | L1, L2 | Offset frequency per satellite |
| **Galileo** | GA | Europe | E1, E5 | High-precision timing, compatible with GPS |
| **SBAS** | SB | Global | L1 | Differential correction (e.g., WAAS, EGNOS) |
| **QZSS** | QZ | Japan / Asia-Pacific | L1, L2, L5 | Augments GPS coverage in Asia |

---

## Signal Strength Guidelines

| **SNR (dB-Hz)** | **Signal Quality** | **Interpretation** |
|------------------|--------------------|--------------------|
| 0–20             | Poor               | Weak or obstructed signal; satellite near horizon or blocked by terrain/buildings. |
| 21–30            | Fair               | Usable but unstable; possible position drift under canopy or indoor conditions. |
| 31–40            | Good               | Reliable tracking; suitable for navigation and timing applications. |
| 41–50            | Very Good          | Strong satellite lock; low multipath interference. |
| >50              | Excellent          | Ideal line-of-sight conditions; maximum precision. |

---

## Practical Notes

- Satellites with **Y** in the `Use` column are part of the current fix calculation.
- Satellites marked **N** may be below the elevation mask or have low SNR.
- **SBAS** satellites (e.g., `SB133`) provide differential corrections for higher positional accuracy (DGPS or WAAS).
- **QZSS** satellites (`QZ1`, `QZ4`) enhance coverage in the Pacific region but may show `N` if corrections are not used.

---

## Summary

The satellite panel of `cgps` provides vital real-time insight into the GNSS environment:

- How many satellites are visible and being used.
- Signal strength and geometry of each satellite.
- Type of GNSS constellation and elevation/azimuth relationships.

Understanding this data helps optimize GPS antenna placement, verify multi-constellation performance, and ensure accurate timing and navigation results.

---

## References

- [gpsd Project Documentation](https://gpsd.gitlab.io/gpsd/)
- [cgps Man Page](https://linux.die.net/man/1/cgps)
- [GNSS Constellation Overview – ESA](https://www.esa.int/Applications/Navigation/Galileo/GNSS_overview)

---

<HR>
<HR>

# 

<HR>
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
<HR>

# DPS310 Pressure Acquisition and Logging: Raspberry Pi 5 vs RP2040 Comparison

This document compares the use of a **Raspberry Pi 5 with Touch Display** and an **RP2040 microcontroller** (e.g., Adafruit Feather RP2040, Raspberry Pi Pico) for **pressure measurement, data logging, and analysis** using the **Adafruit DPS310 barometric pressure sensor**.

---

## System Overview

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

## DPS310 Pressure Acquisition and Data Logging

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

## Recommended Use Cases

| Application | Best Platform | Notes |
|--------------|---------------|-------|
| **Bench-top testing / live analysis** | Raspberry Pi 5 + Touch Display | GUI graphs, Python data analysis tools. |
| **Field logging / kite flight instrumentation** | RP2040 microcontroller | Low power, lightweight, rugged design. |
| **Remote monitoring with network upload** | Raspberry Pi 5 (headless mode) | Use SSH or web dashboard for real-time monitoring. |
| **Battery-powered sensor node** | RP2040 | Run from Li-ion or Li-Po cells for hours or days. |

---

## Example DPS310 Integration

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
## Summary Comparison

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

## Conclusion

Both platforms can successfully acquire and log pressure data using the **Adafruit DPS310**, but their **optimal roles differ**:

- **Raspberry Pi 5 + Touch Display** 
 Ideal for **real-time visualization**, **interactive GUI control**, and **in-depth data analysis** using full Python libraries. 
 Best suited for **laboratory testing**, **bench experiments**, and **development environments**.

- ⚙️ **RP2040 Microcontroller** 
 Optimized for **low-power, lightweight, and portable** field applications such as **kite-borne data logging** or **edge sensing**. 
 Offers deterministic timing, instant startup, and long battery life, making it excellent for autonomous deployments.

> **Recommended Workflow:** 
> Use the **RP2040** to collect data in the field, then transfer the logged CSV files to the **Raspberry Pi 5** for graphical analysis, filtering, and trend evaluation.

---

<HR>
