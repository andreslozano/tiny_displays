#! /usr/bin/env python
#-*- coding: utf-8 -*-

from random import randint, shuffle
import numpy as np
from PIL import Image
import smbus, time
from rgb_lcd import RgbLcd

NAME = "Rgb Lcd i2c screen convert image"
VERSION = "0.0.2"
DATE = "2018 June 11"
AUTHOR = "Andres Lozano a.k.a Loz"
COPYRIGHT = "Copyleft: This is a free work, you can copy, distribute, and modify it under the terms of the Free Art License http://artlibre.org/licence/lal/en/"
URL = "http://hyperficiel.com"
DESCRIPTION = "convert image to 8 specials chars for rgb lcd"

"""
char 0           char 1           char 2            char 3
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,   	X, X, X, X, X,

char 4           char 5           char 6            char 7
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,    X, X, X, X, X,
X, X, X, X, X,   X, X, X, X, X,   X, X, X, X, X,   	X, X, X, X, X,
"""

def getChars(img=None, data=None):
	if img:
		w, h = (20,16)
		img = img.resize((w, h))
		img = img.convert("1") # array of 0 or 255 values
		data = list(img.getdata())
		
	arr = [(x > 0)*1 for x in data] # [1 if x > 1 else x for x in data]
	pixels = np.array(arr)
	pixels = pixels.reshape(64,5)
	
	chars = [[]]*8
	
	for i in range(0, 8):
		line = 0 if i < 4 else 28
		tmp = []
		for j in xrange(0,32,4):
			tmp.extend(pixels[line+i+j].tolist()) 
		chars[i] = tmp[:]
		
	return chars
	
class PatternStruct:
	def __init__(self, width=8, height=8):
		self.width = width
		self.height = height
	
	def get(self):
		data = []
		tmp = []
		for i in xrange(self.height/2):
			w = self.width / 2
			aLeft = ["a"] * randint(0, w)
			bLeft = ["b"] * (w - len(aLeft))
			tmp = aLeft[:] + bLeft[:]
			shuffle(tmp)
			left = tmp[:]
			tmp.reverse()
			right = tmp[:]
			line = left + right
			data.append(line)
		
		top = data[:]
		data.reverse()
		bottom = data[:]
		pattern = top + bottom
		return pattern
		
	def getData(self):
		pattern = []
		data = self.get()
		for arr in data:
			for x in arr:
				pattern.append( (x == "a")*1 )
		
		return pattern

# example code
if __name__=="__main__":
	print "image to lcd"
	bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
	lcd = RgbLcd(bus)
	count = 0
	alt = 0
	try:
		while True:
			alt = alt ^ 1
			if alt:
				# convert image to oled screen
				image = Image.open("mire.png")
				chars = getChars(image)
			else:
				data = PatternStruct(width=20, height=16).getData()
				chars = getChars(data=data)
				count += 1
				
			lcd.clear()
			for i, char in enumerate(chars):
				lcd.createChar(location=i, pattern=char)
			
			lcd.setRGB(rgb=(randint(0, 255), randint(0, 255), randint(0, 255)))
			
			if not alt:
				lcd.setCursor(row=0)
				lcd.showText("pattern "+str(count))
				lcd.pause(1)
				
			if alt:
				lcd.setCursor(row=0, col=6)
				lcd.showSpecialChars(range(4))
				lcd.setCursor(row=1, col=6)
				lcd.showSpecialChars(range(4,8))
			else:
				lcd.setCursor(row=0)
				charList = []
				for i in range(4):
					charList.extend(range(4))
					
				lcd.showSpecialChars(charList)
				
				lcd.setCursor(row=1)
				charList = []
				for i in range(4):
					charList.extend(range(4,8))
					
				lcd.showSpecialChars(charList)
			
			lcd.pause(2)
	except KeyboardInterrupt:
		lcd.noBacklight()
		lcd.clear()
		print "close device"
