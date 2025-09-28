# Kite Altimeter – CircuitPython Project  

This repository contains the **CircuitPython `code.py`** file for the **Kite Altimeter project** (Hardware Version 3, Software Version 10).  

The project runs on an **Adafruit Metro RP2350** and records altitude and related data during kite flights.  

---

## Development Environment  

- **Board:** Adafruit Metro RP2350  
- **Language:** [CircuitPython](https://circuitpython.org/)  
- **IDE:** [Thonny 4.1.4](https://thonny.org/) running on Raspberry Pi P5  
  - A full Raspberry Pi OS install includes Thonny by default.  
- **Library Management:** [Circup](https://github.com/adafruit/circup) was used to install and update the required libraries on the device.  
- **File System Copy:**  
  - The `tree` output shown below was generated on a **Raspberry Pi 5** using a copy of the RP2040’s files.  
  - This provides a reference of the deployed files on the device.  

---

## RP2350 Structure  

The following files and directories as deployed to the Adafruit Metro RP2350:  

```text
.
├── boot_out.txt
├── code.py
├── lib
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
│   ├── adafruit_ds3231.mpy
│   ├── adafruit_ili9341.mpy
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

```

