# Kite Altimeter – CircuitPython Project  

This repository contains the **CircuitPython `code.py`** file for the **Kite Altimeter project** (Hardware Version 1, Software Version 28.  

The project runs on an **Adafruit Feather RP2040** and records altitude and related data during kite flights.  

---

## Development Environment  

- **Board:** Adafruit Feather RP2040  
- **Language:** [CircuitPython](https://circuitpython.org/)  
- **IDE:** [Thonny 4.1.4](https://thonny.org/) running on Raspberry Pi P5  
  - A full Raspberry Pi OS install includes Thonny by default.  
- **Library Management:** [Circup](https://github.com/adafruit/circup) was used to install and update the required libraries on the device.  
- **File System Copy:**  
  - The `tree` output shown below was generated on a **Raspberry Pi 5** using a copy of the RP2040’s files.  
  - This provides a reference of the deployed files on the device.  

---

## Repository Structure  

The repository contains the following files and directories as deployed to the Feather RP2040 Adalogger:  

```text
.
├── boot_out.txt            # Auto-generated CircuitPython boot message
├── code.py                 # Main program (Kite Altimeter v28)
├── lib/                    # CircuitPython libraries
│   ├── adafruit_bitmap_font
│   │   ├── bdf.mpy
│   │   ├── bitmap_font.mpy
│   │   ├── glyph_cache.mpy
│   │   ├── __init__.py
│   │   ├── pcf.mpy
│   │   └── ttf.mpy
│   ├── adafruit_bus_device
│   │   ├── i2c_device.mpy
│   │   ├── __init__.py
│   │   └── spi_device.mpy
│   ├── adafruit_displayio_sh1107.mpy
│   ├── adafruit_display_text
│   │   ├── bitmap_label.mpy
│   │   ├── __init__.mpy
│   │   ├── label.mpy
│   │   ├── outlined_label.mpy
│   │   ├── scrolling_label.mpy
│   │   └── text_box.mpy
│   ├── adafruit_dps310
│   │   ├── advanced.mpy
│   │   ├── basic.mpy
│   │   └── __init__.mpy
│   ├── adafruit_max1704x.mpy
│   ├── adafruit_pcf8523
│   │   ├── clock.mpy
│   │   ├── pcf8523.mpy
│   │   └── timer.mpy
│   ├── adafruit_pixelbuf.mpy
│   ├── adafruit_register
│   │   ├── i2c_bcd_alarm.mpy
│   │   ├── i2c_bcd_datetime.mpy
│   │   ├── i2c_bit.mpy
│   │   ├── i2c_bits.mpy
│   │   ├── i2c_struct_array.mpy
│   │   ├── i2c_struct.mpy
│   │   └── __init__.py
│   ├── adafruit_sdcard.mpy
│   ├── adafruit_ticks.mpy
│   └── neopixel.mpy
├── sd
│   └── placeholder.txt
└── settings.toml

