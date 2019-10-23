# Oled iIIc SSD1327

## Python oled class

![seedstudio Grove-Oled image](https://statics3.seeedstudio.com/images/product/oled1281281.jpg)  
The class **oledSSD1327.py** allow you to show texte and graphics on a  
[seeedstudio oled SSD1327 display 96x96](https://www.seeedstudio.com/Grove-OLED-Display-1.12%26quot%3B-p-824.html) with a Raspberry Pi  
There is an example of code within the class itself  
There is also a script **convert-image-to-oled.py** that convert a picture to an oled binary file  
All this code was tested on a raspberry pi B+  

convert-image-to-oled.py require python PIL and numpy library  

## To configure i2c go to url

https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c  
For better animation (25 frames/sec) set i2c baudrate to 300 kHz (tested on raspi B+)  

```bash
sudo nano /boot/config.txt
```

160000 <=> 100 kHz on raspberry pi B, B+ and Zero  
480000 = 300 kHz  
```bash
remove comment to : dtparam=i2c_arm=on  
add line: dtparam=i2c1_baudrate=480000  
```
**Andres Lozano Gallego a.k.a Loz, 2018.**  
Copyleft: this work is free, you can copy, distribute and modify it  
under the terms of the Free Art License http://www.artlibre.org
