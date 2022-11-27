# esp32-cam-couchdb


Useful commands:
```bash
# upload compiled firmware folowing instructions on: https://lemariva.com/blog/2020/06/micropython-support-cameras-m5camera-esp32-cam-etc
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ~/Documents/micropython/ports/esp32/build-ESP32_CAM/firmware.bin
# upload app and open terminal using ampy tool
ampy --port /dev/ttyUSB0 put main.py ; sudo picocom /dev/ttyUSB0 -b115200

# use Ctrl + A + X to exit from picocom
```
