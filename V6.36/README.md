CircuitPython files for kite altimeter hardware version 6 and software version 36.

Below is copy on the Raspberry Pi P5 of the files on the Adafruit Feather RP2040 Adalogger.
The Raspberry Pi P5 with Thonny 4.1.4 was used to develope the CircuitPython program.
A full install of the Raspberry Pi OS includes Thonny.

Circup was used to download the required libraries in to the  RP204O.


david@rpi500:~/CircuitPython/KiteAltimeterV6/V36 $ tree
.
├── boot_out.txt
├── code.py
├── lib
│   ├── adafruit_bitmap_font
│   │   ├── bdf.mpy
│   │   ├── bitmap_font.mpy
│   │   ├── glyph_cache.mpy
│   │   ├── __init__.py
│   │   ├── lvfontbin.mpy
│   │   ├── pcf.mpy
│   │   └── ttf.mpy
│   ├── adafruit_bno055.mpy
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
│   ├── adafruit_ds3231.mpy
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
│   ├── fs3000.mpy
│   └── neopixel.mpy
├── sd
│   └── placeholder.txt
├── settings.toml
└── System Volume Information
    ├── IndexerVolumeGuid
    └── WPSettings.dat

10 directories, 43 files
david@rpi500:~/CircuitPython/KiteAltimeterV6/V36 $
