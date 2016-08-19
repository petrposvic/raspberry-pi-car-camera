# Raspberry Pi Car Camera

## Install gpsd

Enable and install gps

  * https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi/pi-setup
  * https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi/use-gpsd

  1. edit file /boot/cmdline.txt
  2. remove console=ttyAMA0,115200 and if there, kgdboc=ttyAMA0,115200


    sudo systemctl stop serial-getty@ttyAMA0.service
    sudo systemctl disable serial-getty@ttyAMA0.service 
    sudo apt-get update
    sudo apt-get install gpsd gpsd-clients python-gps
    sudo systemctl stop gpsd.socket
    sudo systemctl disable gpsd.socket
    sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock

Edit /etc/rc.local and add those lines:

    /usr/sbin/gpsd /dev/ttyS0 -F /var/run/gpsd.sock
    /usr/bin/screen -d -m /home/pi/smarthome/car/car.py
