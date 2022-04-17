# esp32-cam-couchdb


Useful commands:
```shell
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ~/Documents/micropython/ports/esp32/build-ESP32_CAM/firmware.bin
esptool.py --port /dev/ttyUSB0 erase_flash

ampy --port /dev/ttyUSB0 put main.py ; sudo picocom /dev/ttyUSB0 -b115200
```
