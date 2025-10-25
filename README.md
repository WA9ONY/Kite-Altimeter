<P align="center"> - <A HREF="https://www.qrz.com/db/WA9ONY">WA9ONY</A> - <A HREF="https://www.youtube.com/@Kites-Flying">YouTube Kites-Flying</A> - <A HREF="https://www.youtube.com/user/DavidAHaworth">YouTube David Haworth</A> - <A HREF="http://www.stargazing.net/david/index.html">Website</A> -
</P>  

<p align="center"><img width="645" height="865" src="/Images/IMG_4266sm.JPEG">
</p>
<p align="center">
Kite altimenter V2 (altitude & temperature) attached to the bridle point of a Bora 7 kite was the first version to fly.  
</p>

<p align="center"><img width="665" height="843" src="/Images/IMG_7039smcrop.JPEG">
</p>
<p align="center">
Kite altimenter V6 (altitude, temperature, 9-DOF & wind velocity) attached to the main spar of a 8' x 4' delta kite.  
</p>

# Kite Altimeter

Kite-Altimeter repositories conatains information and code for thet kite altimeter projects.

Kite [altimeter](https://en.wikipedia.org/wiki/Altimeter) records the kite height above the ground.

<HR>

## Kite Altimeter Versions

<p align="center">     <img width="368" height="534" src="/Images/V1-6sm4.JPEG">
</p>
<p align="center">
Seven altimeters: V1, V2, V3, V4, V5, V6 and V7.<BR>
V1 for development & testing.<BR>
V2, V4, V5 & V6 for kite flying.<BR>
V3 for ground station based on the Adafruint RP2350 Metro.      
</p>

Reasons for different versions.
+ Version 1 was to test the concept. 
+ Version 2 was the frist version designed to fly.
+ Version 3 was created to be a ground station monitoring the change of the barometric pressure during the flight time.
+ Version 4 was designed to be the smallest and lightest. It has no OLED display, just NioPxiel.
+ Version 5 added 9-DOF (degrees of freedom) and air velocity measurements.
+ Version 6 a smaller version of 5 to mount on the main spar of a delta kite.
+ Version 3 was created to be a ground station monitoring the change of the barometric pressure during the flight time and is currently under development. V7 is based on the Raspberry Pi 5 with 5" touch display.

Functions
+ All altimeter versions log data to a 32 GB micro SD card.
+ V1, V2, V4, V5 & V6 [reed relay](https://www.amazon.com/dp/B07YFBQ4HS?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1&th=1) as a user imput that does not require opening the case. The reed relay is connected between ground and DIO 4.
+ V1, V2, V4, V5 & V6 have a voltage divider with two 1 MegOhm resistors as a voltage divider connected to the battery voltage. The reduced voltage is connected to the RP2040 ADC input to monitor the battery voltage.

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
<TD><P><B>
    9-DOF  
    </B></P></TD>
<TD><P><B>
    Wind  
    </B></P></TD>
</TR>

<TR>
<TD>
    V1
</TD>
<TD>
    205 g<BR>7.23&nbspoz
</TD>
<TD>
    7"&nbspx<BR>4.62"&nbspx<BR>1.75"
</TD>  
<TD>
    <A HREF="https://www.adafruit.com/product/328">3.7V<BR>2,500&nbspmAh</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/4884">Feather<BR>RP2040</A>    
</TD>
<TD>
    <A HREF="https://circuitpython.org/">CircuitPython</A>    
</TD>
<TD>    
    <A HREF="https://www.adafruit.com/product/4650">128x64 OLED<BR>FeatherWing</A>        
</TD>    
<TD>
    <A HREF="https://www.adafruit.com/product/2922">Adalogger<BR>FeatherWing</A> 
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/4494">DPS310</A>   
</TD>     
<TD>
    -  
</TD>
<TD>
    -  
</TD>
</TR>

<TR>
<TD>
    V2
</TD>
<TD>
    58 g<BR>2.05&nbspoz
</TD>
<TD>
    1.87"&nbspdia.&nbspx<BR>3.5"
</TD>  
<TD>
    <A HREF="https://www.adafruit.com/product/1578">3.7V<BR>500&nbspmAh</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/5980">Feather<BR>RP2040<BR>Adalogger</A>    
</TD>
<TD>
    <A HREF="https://circuitpython.org/">CircuitPython</A>    
</TD>
<TD>    
    <A HREF="https://www.adafruit.com/product/4650">128x64 OLED<BR>FeatherWing</A>  
</TD>    
<TD>
    <A HREF="https://www.adafruit.com/product/5188">DS3231</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/4494">DPS310</A>   
</TD>     
<TD>
    -    
</TD>
<TD>
    -  
</TD>
</TR>

<TR>
<TD>
    V3
</TD>
<TD>
    276 g<BR>9.74&nbspoz.  
</TD>
<TD>
    7"&nbspx<BR>4.62"&nbspx<BR>1.75"  
</TD>  
<TD>
    <A HREF="https://www.amazon.com/dp/B0F53X2ZL8?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1">2 x 18650</A><BR>3.7V<BR>9,900&nbspmAh 
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/6003">Metro<BR>RP2350</A>    
</TD>
<TD>
    <A HREF="https://circuitpython.org/">CircuitPython</A>    
</TD>
<TD>    
    <A HREF="https://www.adafruit.com/product/1651">2.8" TFT<BR>Touch<BR>Shield</A>  
</TD>    
<TD>
    <A HREF="https://www.adafruit.com/product/5188">DS3231</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/4494">DPS310</A>   
</TD>     
<TD>
    -    
</TD>
<TD>
    -  
</TD>
</TR>

<TR>
<TD>
    V4
</TD>
<TD>
    44 g<BR>1.55&nbspoz. 
</TD>
<TD>
    1.25"&nbspdia.&nbspx<BR>3.75" 
</TD>  
<TD>
    <A HREF="https://www.adafruit.com/product/4236">3.7V<BR>420&nbspmAh</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/5980">Feather<BR>RP2040<BR>Adalogger</A>    
</TD>
<TD>
    <A HREF="https://circuitpython.org/">CircuitPython</A>    
</TD>
<TD>    
    -  
</TD>    
<TD>
    <A HREF="https://www.adafruit.com/product/5188">DS3231</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/4494">DPS310</A>   
</TD>     
<TD>
    -    
</TD>
<TD>
    -  
</TD>
</TR>

<TR>
<TD>
    V5
</TD>
<TD>
    79 g<BR>2.79&nbspoz.
</TD>
<TD>
    1.87"&nbspdia.&nbspx<BR>5.75" 
</TD>  
<TD>
    <A HREF="https://www.adafruit.com/product/1578">3.7V<BR>500&nbspmAh</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/5980">Feather<BR>RP2040<BR>Adalogger</A>    
</TD>
<TD>
    <A HREF="https://circuitpython.org/">CircuitPython</A>    
</TD>
<TD>    
    <A HREF="https://www.adafruit.com/product/5297">128x128 OLED</A>  
</TD>    
<TD>
    <A HREF="https://www.adafruit.com/product/5188">DS3231</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/4494">DPS310</A>   
</TD>     
<TD>
    <A HREF="https://www.adafruit.com/product/4754">BNO085</A> 
</TD>
<TD>
    <A HREF="https://www.sparkfun.com/sparkfun-air-velocity-sensor-breakout-fs3000-1005-qwiic.html">FS3000-1005</A> 
</TD>
</TR>

<TR>
<TD>
    V6
</TD>
<TD>
    74 g<BR>2.61&nbspoz. 
</TD>
<TD>
    3.5"&nbspx<BR>2.5"&nbspx<BR>2"
</TD>  
<TD>
    <A HREF="https://www.adafruit.com/product/1578">3.7V<BR>500&nbspmAh</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/5980">Feather<BR>RP2040<BR>Adalogger</A>    
</TD>
<TD>
    <A HREF="https://circuitpython.org/">CircuitPython</A>    
</TD>
<TD>    
    <A HREF="https://www.adafruit.com/product/5297">128x128 OLED</A>  
</TD>    
<TD>
    <A HREF="https://www.adafruit.com/product/5188">DS3231</A>
</TD>
<TD>
    <A HREF="https://www.adafruit.com/product/4494">DPS310</A>   
</TD>     
<TD>
    <A HREF="https://www.adafruit.com/product/4754">BNO085</A> 
</TD>
<TD>
    <A HREF="https://www.sparkfun.com/sparkfun-air-velocity-sensor-breakout-fs3000-1015-qwiic.html">FS3000-1015</A> 
</TD>
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
<TD>
 
</TD>
<TD>
     
</TD>
</TR>

</TABLE>

<HR>

## Kite Altimeter Hardware Version 1

</P>  
<p align="center">     <img width="528" height="326" src="/Images/V1.JPEG">
</p>

</P>  
<p align="center">     <img width="384" height="450" src="/Images/IMG_8138a.JPEG">
</p>
<p align="center">
Altimeters V1 was used for development & testing..  
</p>

GitHub directory V1.28 contains the CircuitPython code.py for this altimeter.

+ Case is a food container 7" x 4 5/8" x  1 3/4".
+ Li battery 3.7V at 2,500 mAh.
+ 205 g, 7.23 oz.

<HR>

## Kite Altimeter Hardware Version 2

</P>  
<p align="center">     <img width="448" height="384" src="/Images/V2.JPEG">
</p>

GitHub directory V2.11 contains the CircuitPython code.py for this altimeter.

+ Case is a orange pill container 1 7/8" dia. x 3 1/2".
+ Li battery 3.7V at 500 mAh.
+ 58 g, 2.05 oz.

<HR>

## Kite Altimeter Hardware Version 3

</P>  
<p align="center">     <img width="530" height="326" src="/Images/V3.JPEG">
</p>

GitHub directory V3.10 contains the CircuitPython code.py for this altimeter.

+ Case is a small storage container 7" x 4 5/8" x  1 3/4".
+ Two 18650 Li-ion battery 3.7V at 9,900 mAh.
+ 276 g, 9.74 oz.

<HR>

## Kite Altimeter Hardware Version 4

</P>  
<p align="center">     <img width="560" height="308" src="/Images/V4.JPEG">
</p>

GitHub directory V4.12 contains the CircuitPython code.py for this altimeter.

+ Case is a orange pill container 1 1/4" dia. x 3 3/4".
+ Li battery 3.7V at 420 mAh.
+ 44 g, 1.55 oz.

<HR>

## Kite Altimeter Hardware Version 5

</P>  
<p align="center">     <img width="570" height="304" src="/Images/V5.JPEG">
</p>

GitHub directory V5.35 contains the CircuitPython code.py for this altimeter.

+ Case is a orange pill container 1 7/8" dia. x 5 3/4".
+ Li battery 3.7V at 500 mAh.
+ 79 g, 2.79 oz.

<HR>

## Kite Altimeter Hardware Version 6

</P>  
<p align="center">     <img width="356" height="484" src="/Images/V6.JPEG">
</p>

GitHub directory V6.36 contains the CircuitPython code.py for this altimeter.

GitHub directory V6.36data20250823 contains the data log files for Saturday August 23, 2025 at 
[Washington State International Kite Festival](https://en.wikipedia.org/wiki/Washington_State_International_Kite_Festival)
at Long Beach, WA. V6.36 was mounted on the main spar of a 8' x 4' delta kite flying in the Large Kite Area field.

+ Case is a storage container 3 1/2" x 2 1/2" x  2".
+ Li battery 3.7V at 500 mAh.
+ 74 g, 2.61 oz.

<HR>

## Research

Web  pages
+ [ELEVATION  of  KITE](http://becot.info/tako/anglais/etakoteur.htm)
+ [Let's Go Fly a Kite... With an Arduino on It!](https://www.instructables.com/Lets-Go-Fly-a-Kite-With-an-Arduino-on-It/)
+ [Global Positioning System & Telemetry](https://www.kitesite.com.au/kiterecord/gps.html)

Videos
+ Apogee How Altitude Is Measured for Model Rockets, Airplanes and kites tutorial [video](https://youtu.be/PD-4fi0MygI?si=Bojd5ru5muOVsMX8)
+ Apogee rocket altimeter YouTube [videos](https://www.youtube.com/@apogeerockets/search?query=Altimeter)

Wikipedia
+ [Altimeter](https://en.wikipedia.org/wiki/Altimeter)
+ [Pressure altimeter](https://en.wikipedia.org/wiki/Pressure_altimeter)
+ [Density altitude](https://en.wikipedia.org/wiki/Density_altitude)
+ [International Standard Atmosphere](https://en.wikipedia.org/wiki/International_Standard_Atmosphere)
+ [Barometers](https://en.wikipedia.org/wiki/Barometer)


## Altimeter Products
+ Jolly Logic [AltimeterOne](https://jollylogic.com/products/altimeterone/)
  + [Amazon](https://www.amazon.com/dp/B0069ZD53E?psc=1&smid=A2YVVEWGBD4JCX&ref_=chk_typ_imgToDp)
+ Jolly Logic [AltimeterTwo](https://www.apogeerockets.com/Electronics-Payloads/Altimeters/Jolly-Logic-AltimeterTwo)
  + For rockets only
  + [Amazon](https://www.amazon.com/Jolly-Logic-JL-A2-AltimeterTwo/dp/B0069Z6YCI/ref=sr_1_4?crid=39MKX6WIQUY1Z&dib=eyJ2IjoiMSJ9.ghD88zHyqLtrEhXs21qyjydc7m41SSCogII7vzfpp7Ss-c38J4PArjpllElGoflom1-nFifLPNm_YM0otbXgg_YKki784NonDlXA1fmwzkwrG3X1vQyfzRcZA6xoDb4DrFNUiFi3_BMm-9NUbVIUZjOLyJ6AXks8f19g3APV9tavdBc_FHCSiCSUz7pFeXdd_wcs8UXwWHax6fB2qlVxJ2w_yuX6l99wAUt82BYP7Vn1jU0X2xgA-nzoygaMI4WnukyKWs5EQTKm1J0jUhgUwhWgEuDX26_fCgmtnREBtqw.jDE2INQnOJGa1hT3zGFkPjnjFCo6phgFTAzE02sCQfc&dib_tag=se&keywords=altimeter+two&qid=1759088290&s=sporting-goods&sprefix=altimetertwo%2Csporting%2C153&sr=1-4)
+ Estes 2246 Altimeter [Amazon](https://www.amazon.com/dp/B00EZBH896?ref=ppx_yo2ov_dt_b_fed_asin_title)
+ Eronotix [delta altimeter kite](https://eronotix.com/)
+ Rocket.Supplies [Altimeters](https://rocket.supplies/products.php?cat=Altimeters)

## GPS Products with Altitude
+ SKYRC GSM-015 [Amazon](https://www.amazon.com/SKYRC-Speedometer-Altimeter-Tracking-Quadcopter/dp/B07RWL8BTG/ref=sr_1_3?crid=4I6OTCY38YZ8&dib=eyJ2IjoiMSJ9.gAWQdYaikd2XWGnSjA2-ER5Dob_GdE48VjowPcHt77LGjHj071QN20LucGBJIEps.ltLwnXyxA1OfLdlityzxWghwIPCDLOtOQPOrx2-pGpI&dib_tag=se&keywords=skyrc+gsm+020&qid=1759087633&sprefix=GSM-020%2Caps%2C230&sr=8-3)


## AI on kites altimeters

DIY Barometric Logger: For those interested in electronics, a custom altimeter can be built using a microcontroller (such as an Arduino), a barometric pressure sensor, and an SD card module for data logging. This approach is more complex but offers flexibility for advanced users. ([Google AI](https://share.google/aimode/4WKR2bouP8A6tX3Cm))


## Measuring Kite Altitude with Pressure Sensors

A **barometric pressure sensor** measures the surrounding air pressure and infers altitude from the rate of pressure decrease with height. 
As altitude increases, the air becomes thinner, causing a predictable drop in pressure. This relationship follows the **barometric formula** (standard atmosphere approximation):

h = (T₀ / L) · [ 1 − ( P / P₀ )^((R·L)/g) ]

Where:

| Symbol | Meaning | Typical Units |
|:------:|:---------|:--------------|
| h | Altitude above sea level | meters |
| P | Measured pressure | hPa |
| P₀ | Sea-level reference pressure | hPa |
| T₀ | Standard temperature (≈ 288.15 K) | kelvin |
| L | Lapse rate (≈ 0.0065 K/m) | K/m |
| R | Gas constant for air (287 J/kg·K) | — |
| g | Acceleration due to gravity (9.80665 m/s²) | — |

In a kite altimeter, sensors such as the **Adafruit DPS310** or **BMP585** are placed near the kite’s bridle point or along the main spar. 
The onboard microcontroller continuously reads barometric pressure, converts it into altitude, and logs the data along with temperature and motion readings.  
Because atmospheric pressure changes with weather, accurate altitude measurement requires calibration against a **ground reference pressure** — for example, from a second sensor on the ground or a local NOAA weather station.

### Other Methods to Measure Kite Altitude

| Method | How It Works | Advantages | Limitations |
|:--------|:-------------|:------------|:-------------|
| **Barometric (Pressure) Sensor** | Converts air pressure change to altitude. | Lightweight, low power, inexpensive. | Sensitive to weather pressure variation. |
| **GPS Receiver** | Uses satellite trilateration to determine altitude. | Provides absolute altitude; no calibration needed. | Slow update rate (1–10 Hz), higher power draw, noisy vertical accuracy. |
| **Inertial (IMU Integration)** | Integrates acceleration data from a 9‑DOF sensor. | High‑speed data, good for short‑term motion. | Long‑term drift; needs barometric or GPS correction. |
| **Optical Theodolite / Camera Tracking** | Measures elevation angle from the ground. | High reference accuracy. | Requires ground operator and line‑of‑sight. |
| **Tether Geometry** | Combines line length and elevation angle sensors. | Simple mechanical method. | Assumes taut line; ignores catenary sag. |
| **Radar / LIDAR Altimetry** | Measures distance via radio or laser pulse reflection. | Direct and precise. | Heavy, expensive, and power‑hungry. |
| **Acoustic Ranging** | Measures sound pulse travel time. | Simple short‑range measurement. | Limited range (< 100 m) and affected by wind. |

This combination of methods can provide both relative and absolute altitude references for kite flight experiments, depending on mission goals, payload mass, and available power.

<TABLE>
<TR>
<TH>IC type</TH>
<TH>Adafruit Product ID</TH>
<TH>Price (USD)</TH>
<TH>Pressure Range</TH>
<TH>Pressure Accuracy / Tolerance</TH>
<TH>Pressure Resolution / Noise Floor</TH>
<TH>On-Chip Measurement Processing?</TH>
</TR>
<TR>
<TD>BMP585<br>(Bosch)</TD>
<TD><A HREF="https://www.adafruit.com/product/6413">6413</A></TD>
<TD>$14.95</TD>
<TD>300–1250&nbsp;hPa</TD>
<TD>±50&nbsp;Pa absolute (≈±0.5&nbsp;hPa) typical;<BR>±6&nbsp;Pa relative</TD>
<TD>0.08&nbsp;Pa&nbsp;RMS noise (≈0.0008&nbsp;hPa)</TD>
<TD>Yes — factory calibration, digital compensation, oversampling, FIFO buffer</TD>
</TR>
<TR>
<TD>BMP580<br>(Bosch)</TD>
<TD><A HREF="https://www.adafruit.com/product/6411">6411</A></TD>
<TD>$7.95</TD>
<TD>300–1250&nbsp;hPa</TD>
<TD>±50&nbsp;Pa absolute (typ)</TD>
<TD>~0.1&nbsp;Pa-class noise (≈0.001&nbsp;hPa)<BR>24-bit internal ADC</TD>
<TD>Yes — digital filtering, oversampling, FIFO</TD>
</TR>
<TR>
<TD>BMP280<br>(Bosch)</TD>
<TD><A HREF="https://www.adafruit.com/product/2651">2651</A></TD>
<TD>$9.95</TD>
<TD>300–1100&nbsp;hPa</TD>
<TD>±1&nbsp;hPa absolute</TD>
<TD>0.16&nbsp;Pa LSB (0.0016&nbsp;hPa)</TD>
<TD>Yes — factory calibration, oversampling, IIR filter</TD>
</TR>
<TR>
<TD>BME280<br>(Bosch)</TD>
<TD><A HREF="https://www.adafruit.com/product/2652">2652</A></TD>
<TD>$14.95</TD>
<TD>300–1100&nbsp;hPa</TD>
<TD>±1&nbsp;hPa absolute (pressure channel)</TD>
<TD>0.16&nbsp;Pa step (0.0016&nbsp;hPa)</TD>
<TD>Yes — calibrated pressure + temp + humidity with digital compensation</TD>
</TR>
<TR>
<TD>DPS310<br>(Infineon)</TD>
<TD><A HREF="https://www.adafruit.com/product/4494">4494</A></TD>
<TD>$6.95</TD>
<TD>300–1200&nbsp;hPa</TD>
<TD>±1&nbsp;hPa absolute;<BR>±0.002&nbsp;hPa relative (high-precision mode)</TD>
<TD>~0.002&nbsp;hPa (~0.2&nbsp;Pa)<BR>≈2&nbsp;cm altitude steps</TD>
<TD>Yes — internal temperature compensation, oversampling, FIFO</TD>
</TR>
<TR>
<TD>LPS22HB<br>(ST)</TD>
<TD><A HREF="https://www.adafruit.com/product/4633">4633</A></TD>
<TD>$6.95</TD>
<TD>260–1260&nbsp;hPa</TD>
<TD>±0.1&nbsp;hPa after 1-point calibration<BR>(≈±1&nbsp;hPa before)</TD>
<TD>~0.01&nbsp;hPa RMS<BR>24-bit pressure data @ up to ~75&nbsp;Hz</TD>
<TD>Yes — on-chip compensation, oversampling, FIFO</TD>
</TR>
<TR>
<TD>LPS25HB<br>(ST)</TD>
<TD><A HREF="https://www.adafruit.com/product/4530">4530</A></TD>
<TD>$9.95</TD>
<TD>260–1260&nbsp;hPa</TD>
<TD>±0.2&nbsp;hPa (after calibration)</TD>
<TD>~0.01&nbsp;hPa RMS<BR>24-bit pressure data</TD>
<TD>Yes — digital interface with built-in calibration &amp; FIFO</TD>
</TR>
<TR>
<TD>LPS35HW / LPS33HW<br>(ST, water-resistant)</TD>
<TD><A HREF="https://www.adafruit.com/product/4258">4258</A> (LPS35HW)<BR><A HREF="https://www.adafruit.com/product/4414">4414</A> (LPS33HW)</TD>
<TD>$12.50</TD>
<TD>~260–1260&nbsp;hPa</TD>
<TD>±0.1–0.2&nbsp;hPa class (typ)</TD>
<TD>~0.01&nbsp;hPa-class noise</TD>
<TD>Yes — compensated digital output; gel-filled cavity for water / chemical resistance</TD>
</TR>
<TR>
<TD>MPL3115A2<br>(NXP)</TD>
<TD><A HREF="https://www.adafruit.com/product/1893">1893</A></TD>
<TD>$14.95</TD>
<TD>50–110&nbsp;kPa<br>(500–1100&nbsp;hPa equiv)</TD>
<TD>±1&nbsp;m altitude / ±1&nbsp;hPa class typical</TD>
<TD>1.5&nbsp;Pa (~0.015&nbsp;hPa)<BR>≈0.3&nbsp;m altitude resolution</TD>
<TD>Yes — integrated altimeter mode, I2C digital output, internal compensation</TD>
</TR>
<TR>
<TD>BMP388 / BMP390<br>(Bosch)</TD>
<TD><A HREF="https://www.adafruit.com/product/3966">3966</A> (BMP388)</TD>
<TD>$9.95 (BMP388)</TD>
<TD>300–1250&nbsp;hPa (typ)</TD>
<TD>±8&nbsp;Pa relative (≈±0.08&nbsp;hPa)<BR>≈±0.5&nbsp;m altitude</TD>
<TD>Altitude noise ≈0.1&nbsp;m<BR>(≈0.01–0.02&nbsp;hPa)</TD>
<TD>Yes — digital compensation, oversampling, IIR filtering, I2C/SPI</TD>
</TR>
<TR>
<TD>SPA06-003<br>(Goertek)</TD>
<TD><A HREF="https://www.adafruit.com/product/6420">6420</A></TD>
<TD>$4.95</TD>
<TD>300–1100&nbsp;hPa<BR>(≈-500&nbsp;m to +9000&nbsp;m altitude)</TD>
<TD>±30&nbsp;Pa absolute (≈±0.3&nbsp;hPa)<BR>±3&nbsp;Pa relative (≈±0.03&nbsp;hPa)</TD>
<TD>Not publicly specified; 24-bit digital pressure + temp readout</TD>
<TD>Yes — built-in regulator &amp; level shifting, factory calibration, I2C ready</TD>
</TR>
<TR>
<TD>MPRLS (Honeywell die + ADC)</TD>
<TD><A HREF="https://www.adafruit.com/product/3965">3965</A></TD>
<TD>$29.95</TD>
<TD>0–25&nbsp;PSI absolute<BR>(~0–172&nbsp;kPa)</TD>
<TD>Factory calibrated absolute pressure; designed for medical / assistive tech range</TD>
<TD>24-bit compensated digital output (&lt;&lt;1&nbsp;Pa effective step over range)</TD>
<TD>Yes — gel-covered sensing element, on-chip 24-bit ADC &amp; temperature compensation</TD>
</TR>
</TABLE>

<hr>

## Notes & Context for Your Edge‑Microcontroller / Kite‑Logger Projects

- The DPS310 and BMP585 sensors offer the **highest resolution** and are ideal for precise altitude logging in kite‑borne instruments, where vertical motion on the order of centimeters matters.
- The **LPS22HB / LPS25HB / LPS35HW** series from STMicroelectronics provide excellent accuracy with low power use and environmental sealing (LPS35HW) for damp or coastal conditions.
- **Bosch BMP/BME series** (BMP280, BME280, BMP388/390, BMP580/585) remain popular for general atmospheric logging — they provide reliable factory‑calibrated output, easy integration over I²C/SPI, and consistent results across wide temperature ranges.
- The **MPL3115A2** from NXP adds a built‑in altitude conversion mode, useful when the host MCU has limited resources for floating‑point math.
- **MPRLS** (Honeywell) is a ported, absolute‑pressure device suitable for sealed enclosures or airflow/tube measurements — not typically for open‑air atmospheric use.
- For kite systems, **oversampling and filtering** should be tuned to match flight dynamics. Excessive filtering can mask short‑term gusts or tether vibration signatures, while minimal filtering may amplify noise.
- Mount sensors in a **well‑ventilated but shaded enclosure** to minimize thermal drift from sun exposure and prevent condensation from rapid humidity changes.
- Log barometric pressure together with **temperature, humidity, IMU, and wind velocity** to correlate atmospheric and mechanical behavior during flight.
- For long‑duration flights, use **non‑blocking I²C reads** and efficient data logging to microSD; verify timestamps remain synchronized if your system lacks a real‑time clock (RTC).

These considerations provide a foundation for building high‑resolution, reliable kite data‑logging instruments integrating Adafruit atmospheric sensors with edge microcontrollers.
