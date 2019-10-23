#! /usr/bin/env python
#-*- coding: utf-8 -*-

import numpy as np
import sys, os
from PIL import Image

NAME = "Oled SSD1308 i2c screen convert image"
VERSION = "0.0.3"
DATE = "2018 April 22"
AUTHOR = "Andres Lozano a.k.a Loz"
COPYRIGHT = "Copyleft: This is a free work, you can copy, distribute, and modify it under the terms of the Free Art License http://artlibre.org/licence/lal/en/"
URL = "http://hyperficiel.com"
DESCRIPTION = "convert image to seeedstudio oled display 128x64 SSD1308, usage: python image2bin.py filename"

"""
Image to Oled screen: example with 96 x 96 pixels screen
	|		page 		0		|		|		page		1		|	...	12	pages
	0	1	2	3	4	5	6	7		8	9	10	11	12	13	14	15	... 96	bytes
0	byt	byt	byt	byt	byt	byt	byt	byt		byt	byt	byt	byt	byt	byt	byt	byt	...
	0	x	x	x	x	x	x	x		x	x	x	x	x	x	x	x	...	LSB bits order
	1	x	x	x	x	x	x	x		x	x	x	x	x	x	x	x	... each bit equal one pixel
	2	x	x	x	x	x	x	x		x	x	x	x	x	x	x	x	...
	3	x	x	x	x	x	x	x		x	x	x	x	x	x	x	x	...
	4	x	x	x	x	x	x	x		x	x	x	x	x	x	x	x	...
	5	x	x	x	x	x	x	x		x	x	x	x	x	x	x	x	...
	6	x	x	x	x	x	x	x		x	x	x	x	x	x	x	x	...
	7	x	x	x	x	x	x	x		x	x	x	x	x	x	x	x	...
1	byt	byt	byt	byt	byt	byt	byt	byt		byt	byt	byt	byt	byt	byt	byt	byt	...
2	byt	byt	byt	byt	byt	byt	byt	byt		byt	byt	byt	byt	byt	byt	byt	byt	...
3	byt	byt	byt	byt	byt	byt	byt	byt		byt	byt	byt	byt	byt	byt	byt	byt	...
4	byt	byt	byt	byt	byt	byt	byt	byt		byt	byt	byt	byt	byt	byt	byt	byt	...
5	byt	byt	byt	byt	byt	byt	byt	byt		byt	byt	byt	byt	byt	byt	byt	byt	...
7	byt	byt	byt	byt	byt	byt	byt	byt		byt	byt	byt	byt	byt	byt	byt	byt	...
8	byt	byt	byt	byt	byt	byt	byt	byt		byt	byt	byt	byt	byt	byt	byt	byt	...	12    rows
"""
def getBytes(img=None):
	# You can convert a batch of files using this function to a list of files
	w, h = (96,96)
	img = img.resize((w, h))
	img = img.convert("1") # array of 0 or 255 values
	pixels = np.array(list(img.getdata()))
	lcdRows = pixels.reshape(h / 8, w * 8) # 8 vertical pixels by byte
	
	bytes = []
	for lcdRow in lcdRows:
		lcdRow = lcdRow.reshape(8, w)
		bits = np.array([str((x > 0)*1) for x in lcdRow.flatten('F')]) # fortran style, take 8 pixels vertical to make a array of bits
		arrays_of_bits = bits.reshape(w, 8) # ex: width * array of 8 bits
		bytes.extend([int(''.join(x[::-1]),2) for x in arrays_of_bits]) # add bytes array of bits reversed and convert them to int
		
	return bytes

if __name__ == "__main__":
	if len(sys.argv) > 1:
		file = sys.argv[1]
		dir = os.path.dirname(file)
		base, ext = os.path.splitext(sys.path.basename(file))
	else:
		file = "bacall.png"
		dir = os.path.dirname(os.path.realpath(__file__))
		base = "bacall"
	
	print dir
	# convert image to oled screen
	image = Image.open(file)
	bytes = getBytes(image)
	file = os.path.join(dir, base+".bin")
	with open(file,"wb") as f:
		f.write(bytearray(bytes))
