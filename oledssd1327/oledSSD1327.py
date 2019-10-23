#! /usr/bin/env python
#-*- coding: utf-8 -*-
import smbus, time, textwrap

# He andado muchos caminos, 
# he abierto muchas veredas; 
# he navegado en cien mares, 
# y atracado en cien riberas. 

NAME = "Oled SSD1327 i2c screen"
VERSION = "0.0.1"
DATE = "2018 October 25"
AUTHOR = "Andres Lozano a.k.a Loz"
COPYRIGHT = "Copyleft: This is a free work, you can copy, distribute, and modify it under the terms of the Free Art License http://artlibre.org/licence/lal/en/"
URL = "http://hyperficiel.com"
DESCRIPTION = "Seeedstudio oled display 96x96 SSD1327"

class OledSSD1327:
	def __init__(self, bus=None):
		"""
		to configure i2c go to url
		https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
		For better animation set i2c baudrate to 300 kHz (tested on raspi B+) and a framerate of 6 image per second
		160000 = 100 kHz on last raspi B, B+ and Zero W
		edit: sudo nano /boot/config.txt
		after set to "on" : dtparam=i2c_arm=on
		add line: dtparam=i2c1_baudrate=480000
		"""
		self.OLED_Address = 0x3c # 7 bit address (will be left shifted to add the read write bit)
		self.OLED_Command_Mode = 0x80
		self.OLED_Data_Mode = 0x40
		self.OLED_Display_Off = 0xae
		self.OLED_Display_On = 0xaf
		self.OLED_Normal_Display = 0xa4
		self.OLED_Inverse_Display = 0xa7
		self.OLED_Activate_Scroll = 0x2f
		self.OLED_Desactivate_Scroll = 0x2e
		self.OLED_Set_Brightness = 0x81

		self.OLED_Scroll_Left = 0x26
		self.OLED_Scroll_Right = 0x27

		self.OLED_Scroll_2Frames = 0x7
		self.OLED_Scroll_3Frames = 0x4
		self.OLED_Scroll_4Frames = 0x5
		self.OLED_Scroll_5Frames = 0x0
		self.OLED_Scroll_25Frames = 0x6
		self.OLED_Scroll_64Frames = 0x1
		self.OLED_Scroll_128Frames = 0x2
		self.OLED_Scroll_256Frames = 0x3

		self.NULLBYTE = 0x00
		self.FFBYTE = 0xff

		self.bus = bus
		
		self.grayH = 0xf0
		self.grayL = 0x0f
		
		# text values
		self.ascii = self.getAscii()
		self.align = 0
		
		# screen values
		self.oled_width = 96
		self.oled_height = 96
		self.oled_rows = self.oled_height / 8 # 8 pixels by row
		self.oled_data_size = (self.oled_width * self.oled_rows) # assume 8192 pixels => 1024 bytes (8 pixels by bytes)
	
	# Init function of the OLED
	def init_OLED(self):
		blk=[0xFD]       # Unlock OLED driver IC MCU interface from entering command. i.e: Accept commands
		blk.append(0x12)
		blk.append(0xAE) # Set display off
		blk.append(0xA8) # set multiplex ratio
		blk.append(0x5F) # 96
		blk.append(0xA1) # set display start line
		blk.append(0x00)
		blk.append(0xA2) # set display offset
		blk.append(0x60)
		blk.append(0xA0) # set remap
		blk.append(0x46)
		blk.append(0xAB) # set vdd internal
		blk.append(0x01) #
		blk.append(0x81) # set contrasr
		blk.append(0x53) # 100 nit
		blk.append(0xB1) # Set Phase Length
		blk.append(0X51) #
		blk.append(0xB3) # Set Display Clock Divide Ratio/Oscillator Frequency
		blk.append(0x01)
		blk.append(0xB9) #
		blk.append(0xBC) # set pre_charge voltage/VCOMH
		blk.append(0x08) # (0x08)
		blk.append(0xBE) # set VCOMH
		blk.append(0X07) # (0x07)
		blk.append(0xB6) # Set second pre-charge period
		blk.append(0x01) #
		blk.append(0xD5) # enable second precharge and enternal vsl
		blk.append(0X62) # (0x62)
		blk.append(0xA4) # Set Normal Display Mode
		blk.append(0x2E) # Deactivate Scroll
		blk.append(0xAF) # Switch on display
		self.writeCommand(blk)
		
		time.sleep(0.1)

		# Row Address
		blk=[0x75]       # Set Row Address
		blk.append(0x00) # Start 0
		blk.append(0x5f) # End 95
		# Column Address
		blk.append(0x15) # Set Column Address
		blk.append(0x08) # Start from 8th Column of driver IC. This is 0th Column for OLED
		blk.append(0x37) # End at (8 + 47)th column. Each Column has 2 pixels(segments)
		self.writeCommand(blk)
				
	def clearDisplay(self):
		# fill all screen with null bytes
		nullDataBlock = [0] * 32
		self.setRowCol(row=0, col=0) # go to (0,0)
		self.horizontalMode()
		for i in xrange(144): # faster method
			self.writeData(nullDataBlock)
			
		self.setPageMode()

	def showTextAt(self, string="", row=0, col=0, align="left", fill=1): # align: left, center, right; fill: fill row
		length = (16 - col)
		if len(string) > length: # over screen
			for line in textwrap.wrap(string, length):
				line = self.alignText(string=line, align=align, col=col, fill=fill)
				self.setRowCol(row=row, col=col)
				self.putText(string=line)
				row += 1
				if row == 8: row = 0
		else:
			string = self.alignText(string=string, align=align, col=col, fill=fill)
			self.setRowCol(row=row, col=col)
			self.putText(string=string)
				
	def showPageAt(self, row=0, col=0, data=None):
		if type(data).__name__ == "list" and len(data) == 64:
			page = self.getPageFromPixels(data)
		elif  type(data).__name__ == "list" and len(data) == 8:
			page = data
		elif type(data).__name__ == "str" and len(data) == 8:
			page = map(ord, data)
		else:
			# null page
			page = [0] * 8
			
		self.setRowCol(row=row, col=col)
		self.putPage(page)

	def setRowCol(self, row=0, col=0):
		self.writeCommand(0x15)             # Set Column Address
		self.writeCommand(0x08+(col*4))  	# Start Column: Start from 8
		self.writeCommand(0x37)             # End Column
		# Row Address
		self.writeCommand(0x75)             # Set Row Address
		self.writeCommand(0x00+(row*8))     # Start Row
		self.writeCommand(0x07+(row*8))     # End Row
		
	def showImage(self, file=None, data=None):
		return fillScreen(file=None, data=None)
		
	def fillScreen(self, file=None, data=None):
		# file must be an bytearray/binary file
		if file and file.endswith(".bin"):# file priority
			try:
				with open(file, "rb") as f:
					data = map(ord, f.read())
			except:
				print "can't open file",file
				return 0
		
		if type(data).__name__ == "list" and len(data) == self.oled_data_size:# data must be an array of 1152 bytes
			self.setRowCol(row=0, col=0) # go to (0,0)
			line = 0
			for i in xrange(0, self.oled_data_size, 8):
				if i and i % 96 == 0:
					line +=1
					self.setRowCol(row=line, col=0)
				
				self.putPage(data[i:i+8])
		else:
			print "bad data size"
			return 0
			
		return 1

	def setScroll(self, to="right", startRow=0, endRow=11, startCol=0, endCol=11, speed=2):
		# start-end row and col : 0 - 11
		# speed: 2 frames is the fastest, 256 frames is the slowest
		startRow = startRow * 8 # convert to oled page
		endRow = (endRow * 8) + 7
		startCol = startCol * 4
		endCol = (endCol * 4) + 3
		speed = str(speed)
		speedList = {
			"2":self.OLED_Scroll_2Frames, "3":self.OLED_Scroll_3Frames, "4":self.OLED_Scroll_4Frames, 
			"5":self.OLED_Scroll_5Frames, "25":self.OLED_Scroll_25Frames, "64":self.OLED_Scroll_64Frames, 
			"128":self.OLED_Scroll_128Frames, "256":self.OLED_Scroll_256Frames
		}
		if speed in speedList.keys():
			if to == "left": # go to the left
				self.writeCommand([self.OLED_Scroll_Left , self.NULLBYTE, startRow, speedList[speed], endRow, startCol+8, endCol+8, self.NULLBYTE])	
			else:    # go to the right
				self.writeCommand([self.OLED_Scroll_Right, self.NULLBYTE, startRow, speedList[speed], endRow, startCol+8, endCol+8, self.NULLBYTE])
		else:
			print "error speed",speed
			
	def activeScroll(self):
		self.writeCommand(self.OLED_Activate_Scroll)
			
	def desactiveScroll(self):
		self.writeCommand(self.OLED_Desactivate_Scroll)
		
	def setBrightness(self, value=0):
		# values 0 - 15
		self.grayH = (value << 4) & 0xF0
		self.grayL =  value & 0x0F
		
	def inverseDisplay(self):
		self.writeCommand(self.OLED_Inverse_Display) # set inverse Display
		
	def normalDisplay(self):
		self.writeCommand(self.OLED_Normal_Display) # set Normal Display (default)
		
	def setPageMode(self):
		self.writeCommand(0xA0)	# remap to
		self.writeCommand(0x46)	# Vertical mode

	def horizontalMode(self):
		self.writeCommand(0xA0)	# remap to
		self.writeCommand(0x42)	# horizontal mode

		# Row Address
		self.writeCommand(0x75)	# Set Row Address 
		self.writeCommand(0x00)	# Start 0
		self.writeCommand(0x5f)	# End 95 

		# Column Address
		self.writeCommand(0x15)	# Set Column Address 
		self.writeCommand(0x08)	# Start from 8th Column of driver IC. This is 0th Column for OLED 
		self.writeCommand(0x37)	# End at  (8 + 47)th column. Each Column has 2 pixels(or segments)

	# sub functions			
	def writeData(self, dat=None):
		if type(dat).__name__ == "list" and len(dat) <= 32:
			self.bus.write_i2c_block_data(self.OLED_Address, self.OLED_Data_Mode, dat)
		elif type(dat).__name__ == "int":
			self.bus.write_byte_data(self.OLED_Address, self.OLED_Data_Mode, dat)

	def writeCommand(self, cmd=None):
		if type(cmd).__name__ == "list":
			for byte in cmd:
				self.bus.write_byte_data(self.OLED_Address, self.OLED_Command_Mode, byte)
		elif type(cmd).__name__ == "int":
			self.bus.write_byte_data(self.OLED_Address, self.OLED_Command_Mode, cmd)
			
	def getPageFromPixels(self, pixels=None):
		"""
		return array of 8 bytes from 64 pixels description ex:
		pixels = [ # heart
			0, 0, 0, 0, 0, 0, 0, 0,
			0, 1, 1, 0, 1, 1, 0, 0,
			1, 1, 1, 1, 1, 1, 1, 0,
			1, 1, 1, 1, 1, 1, 1, 0,
			0, 1, 1, 1, 1, 1, 0, 0,
			0, 0, 1, 1, 1, 0, 0, 0,
			0, 0, 0, 1, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0
		]
		"""
		bytes = []
		if len(pixels) == 64:
			for x in xrange(8):
				col = []
				for y in xrange(8):
					col.append(pixels[x+(y*8)])
					
				bytes.append(int("".join([str(pix) for pix in col[::-1]]), 2))
		else:
			print "error list len"
			bytes = [0] * 8
				
		return bytes
		
	def putPage(self, arr=[]):
		chars = self.getPage(arr)
		self.writeData(chars)
				
	def getPage(self, arr=[]):
		bytes = []
		for i in [0,2,4,6]: #xrange(0,8,2):
			for j in [0,1,2,3,4,5,6,7]: #xrange(0,8):
				byte = 0x00
				bit1 = ( (arr[i]) >>j ) & 0x01
				bit2 = ( (arr[i+1]) >>j ) & 0x01
				if bit1:
					byte = byte | self.grayH
				else:
					byte = byte | 0x00
					
				if bit2:
					byte = byte | self.grayL
				else:
					byte = byte | 0x00
					
				bytes.append(byte)
		
		# 8 => 32 bytes			
		return bytes
		
	def putChar(self, char):
		if ord(char) > 127:
			index = ord(" ")
		else:
			index = ord(char)
			
		self.putPage(self.ascii[index])
	
	def putText(self, string=None):
		for char in string:
			self.putChar(char)
			
	def alignText(self, string="", align="left", col=0, fill=1):
		length = len(string)
		if fill: # fill row
			if align == "center": 
				f = "{:^"+str(12 - col)+"}"
				return f.format(string)
			elif align == "right":
				f = "{:>"+str(12 - col)+"}"
				return f.format(string)
			else: # left
				f = "{:"+str(12 - col)+"}"
				return f.format(string)
		else: # change col pos
			if align == "center":
				col = ((12 - col - length) / 2) + col
				return string
			elif align == "right":
				col = 12 - length
				return string
			else:
				return string
	
	def getAscii(self):
		# ascii font
		ascii = [[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]] * 32
		ascii.extend([
			[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], # space
			[0x00,0x00,0x5F,0x00,0x00,0x00,0x00,0x00], # ! 	exclamation mark
			[0x00,0x00,0x07,0x00,0x07,0x00,0x00,0x00], # " 	double quote
			[0x00,0x14,0x7F,0x14,0x7F,0x14,0x00,0x00], # # 	number
			[0x00,0x24,0x2A,0x7F,0x2A,0x12,0x00,0x00], # $ 	dollar
			[0x00,0x23,0x13,0x08,0x64,0x62,0x00,0x00], # % 	percent
			[0x00,0x36,0x49,0x55,0x22,0x50,0x00,0x00], # & 	ampersand
			[0x00,0x00,0x05,0x03,0x00,0x00,0x00,0x00], # ' 	single quote
			[0x00,0x1C,0x22,0x41,0x00,0x00,0x00,0x00], # ( 	left parenthesis
			[0x00,0x41,0x22,0x1C,0x00,0x00,0x00,0x00], # ) 	right parenthesis
			[0x00,0x08,0x2A,0x1C,0x2A,0x08,0x00,0x00], # * 	asterisk
			[0x00,0x08,0x08,0x3E,0x08,0x08,0x00,0x00], # + 	plus
			[0x00,0xA0,0x60,0x00,0x00,0x00,0x00,0x00], # , 	comma
			[0x00,0x08,0x08,0x08,0x08,0x08,0x00,0x00], # - 	minus
			[0x00,0x60,0x60,0x00,0x00,0x00,0x00,0x00], # . 	period
			[0x00,0x20,0x10,0x08,0x04,0x02,0x00,0x00], # / 	slash
			[0x00,0x3E,0x51,0x49,0x45,0x3E,0x00,0x00], # 0 	zero
			[0x00,0x00,0x42,0x7F,0x40,0x00,0x00,0x00], # 1 	one
			[0x00,0x62,0x51,0x49,0x49,0x46,0x00,0x00], # 2 	two
			[0x00,0x22,0x41,0x49,0x49,0x36,0x00,0x00], # 3 	three
			[0x00,0x18,0x14,0x12,0x7F,0x10,0x00,0x00], # 4 	four
			[0x00,0x27,0x45,0x45,0x45,0x39,0x00,0x00], # 5 	five
			[0x00,0x3C,0x4A,0x49,0x49,0x30,0x00,0x00], # 6 	six
			[0x00,0x01,0x71,0x09,0x05,0x03,0x00,0x00], # 7 	seven
			[0x00,0x36,0x49,0x49,0x49,0x36,0x00,0x00], # 8 	eight
			[0x00,0x06,0x49,0x49,0x29,0x1E,0x00,0x00], # 9 	nine
			[0x00,0x00,0x36,0x36,0x00,0x00,0x00,0x00], # : 	colon
			[0x00,0x00,0xAC,0x6C,0x00,0x00,0x00,0x00], # ; 	semicolon
			[0x00,0x08,0x14,0x22,0x41,0x00,0x00,0x00], # < 	less than
			[0x00,0x14,0x14,0x14,0x14,0x14,0x00,0x00], # = 	equality sign
			[0x00,0x41,0x22,0x14,0x08,0x00,0x00,0x00], # > 	greater than
			[0x00,0x02,0x01,0x51,0x09,0x06,0x00,0x00], # ? 	question mark
			[0x00,0x32,0x49,0x79,0x41,0x3E,0x00,0x00], # @ 	at sign
			[0x00,0x7E,0x09,0x09,0x09,0x7E,0x00,0x00], # A 	 
			[0x00,0x7F,0x49,0x49,0x49,0x36,0x00,0x00], # B 	 
			[0x00,0x3E,0x41,0x41,0x41,0x22,0x00,0x00], # C 	 
			[0x00,0x7F,0x41,0x41,0x22,0x1C,0x00,0x00], # D 	 
			[0x00,0x7F,0x49,0x49,0x49,0x41,0x00,0x00], # E 	 
			[0x00,0x7F,0x09,0x09,0x09,0x01,0x00,0x00], # F 	 
			[0x00,0x3E,0x41,0x41,0x51,0x72,0x00,0x00], # G 	 
			[0x00,0x7F,0x08,0x08,0x08,0x7F,0x00,0x00], # H 	 
			[0x00,0x41,0x7F,0x41,0x00,0x00,0x00,0x00], # I 	 
			[0x00,0x20,0x40,0x41,0x3F,0x01,0x00,0x00], # J 	 
			[0x00,0x7F,0x08,0x14,0x22,0x41,0x00,0x00], # K 	 
			[0x00,0x7F,0x40,0x40,0x40,0x40,0x00,0x00], # L 	 
			[0x00,0x7F,0x02,0x0C,0x02,0x7F,0x00,0x00], # M 	 
			[0x00,0x7F,0x04,0x08,0x10,0x7F,0x00,0x00], # N 	 
			[0x00,0x3E,0x41,0x41,0x41,0x3E,0x00,0x00], # O 	 
			[0x00,0x7F,0x09,0x09,0x09,0x06,0x00,0x00], # P 	 
			[0x00,0x3E,0x41,0x51,0x21,0x5E,0x00,0x00], # Q 	 
			[0x00,0x7F,0x09,0x19,0x29,0x46,0x00,0x00], # R 	 
			[0x00,0x26,0x49,0x49,0x49,0x32,0x00,0x00], # S 	 
			[0x00,0x01,0x01,0x7F,0x01,0x01,0x00,0x00], # T 	 
			[0x00,0x3F,0x40,0x40,0x40,0x3F,0x00,0x00], # U 	 
			[0x00,0x1F,0x20,0x40,0x20,0x1F,0x00,0x00], # V 	 
			[0x00,0x3F,0x40,0x38,0x40,0x3F,0x00,0x00], # W 	 
			[0x00,0x63,0x14,0x08,0x14,0x63,0x00,0x00], # X 	 
			[0x00,0x03,0x04,0x78,0x04,0x03,0x00,0x00], # Y 	 
			[0x00,0x61,0x51,0x49,0x45,0x43,0x00,0x00], # Z 	 
			[0x00,0x7F,0x41,0x41,0x00,0x00,0x00,0x00], # [ 	left square bracket
			[0x00,0x02,0x04,0x08,0x10,0x20,0x00,0x00], # \ 	backslash
			[0x00,0x41,0x41,0x7F,0x00,0x00,0x00,0x00], # ] 	right square bracket
			[0x00,0x04,0x02,0x01,0x02,0x04,0x00,0x00], # ^ 	caret / circumflex
			[0x00,0x80,0x80,0x80,0x80,0x80,0x00,0x00], # _ 	underscore
			[0x00,0x01,0x02,0x04,0x00,0x00,0x00,0x00], # ` 	grave / accent
			[0x00,0x20,0x54,0x54,0x54,0x78,0x00,0x00], # a 	 
			[0x00,0x7F,0x48,0x44,0x44,0x38,0x00,0x00], # b 	 
			[0x00,0x38,0x44,0x44,0x28,0x00,0x00,0x00], # c 	 
			[0x00,0x38,0x44,0x44,0x48,0x7F,0x00,0x00], # d 	 
			[0x00,0x38,0x54,0x54,0x54,0x18,0x00,0x00], # e 	 
			[0x00,0x08,0x7E,0x09,0x02,0x00,0x00,0x00], # f 	 
			[0x00,0x18,0xA4,0xA4,0xA4,0x7C,0x00,0x00], # g 	 
			[0x00,0x7F,0x08,0x04,0x04,0x78,0x00,0x00], # h 	 
			[0x00,0x00,0x7D,0x00,0x00,0x00,0x00,0x00], # i 	 
			[0x00,0x80,0x84,0x7D,0x00,0x00,0x00,0x00], # j 	 
			[0x00,0x7F,0x10,0x28,0x44,0x00,0x00,0x00], # k 	 
			[0x00,0x41,0x7F,0x40,0x00,0x00,0x00,0x00], # l 	 
			[0x00,0x7C,0x04,0x18,0x04,0x78,0x00,0x00], # m 	 
			[0x00,0x7C,0x08,0x04,0x7C,0x00,0x00,0x00], # n 	 
			[0x00,0x38,0x44,0x44,0x38,0x00,0x00,0x00], # o 	 
			[0x00,0xFC,0x24,0x24,0x18,0x00,0x00,0x00], # p 	 
			[0x00,0x18,0x24,0x24,0xFC,0x00,0x00,0x00], # q 	 
			[0x00,0x00,0x7C,0x08,0x04,0x00,0x00,0x00], # r 	 
			[0x00,0x48,0x54,0x54,0x24,0x00,0x00,0x00], # s 	 
			[0x00,0x04,0x7F,0x44,0x00,0x00,0x00,0x00], # t 	 
			[0x00,0x3C,0x40,0x40,0x7C,0x00,0x00,0x00], # u 	 
			[0x00,0x1C,0x20,0x40,0x20,0x1C,0x00,0x00], # v 	 
			[0x00,0x3C,0x40,0x30,0x40,0x3C,0x00,0x00], # w 	 
			[0x00,0x44,0x28,0x10,0x28,0x44,0x00,0x00], # x 	 
			[0x00,0x1C,0xA0,0xA0,0x7C,0x00,0x00,0x00], # y 	 
			[0x00,0x44,0x64,0x54,0x4C,0x44,0x00,0x00], # z 	 
			[0x00,0x08,0x36,0x41,0x00,0x00,0x00,0x00], # { 	left curly bracket
			[0x00,0x00,0x7F,0x00,0x00,0x00,0x00,0x00], # | 	vertical bar
			[0x00,0x41,0x36,0x08,0x00,0x00,0x00,0x00], # } 	right curly bracket
			[0x00,0x02,0x01,0x01,0x02,0x01,0x00,0x00], # ~ 	tilde
			[0x00,0x02,0x05,0x05,0x02,0x00,0x00,0x00]  # DEL 	delete
		])
		return ascii
		
if __name__ == "__main__":
	print "you are in class OledSSD1327"
	bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
	oled = OledSSD1327(bus)
	oled.init_OLED()
	
	heartPixels = [ # page pixels description
			0, 0, 0, 0, 0, 0, 0, 0,
			0, 1, 1, 0, 1, 1, 0, 0,
			1, 1, 1, 1, 1, 1, 1, 0,
			1, 1, 1, 1, 1, 1, 1, 0,
			0, 1, 1, 1, 1, 1, 0, 0,
			0, 0, 1, 1, 1, 0, 0, 0,
			0, 0, 0, 1, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0
		]
	heartBytes = b'\x0c\x1e\x3e\x7c\x3e\x1e\x0c\x00'	# same by bytes
	heartInts = [12, 30, 62, 124, 62, 30, 12, 0]		# same by ints
	
	try:
		while True:
			oled.normalDisplay()
			oled.clearDisplay()
			time.sleep(1)
			row = 3
			# intro text
			for i in xrange(12): # fill row
				oled.showPageAt(row=row+1, col=i, data=heartPixels)
			
			oled.showPageAt(row=row+2, col=0,  data=heartInts)
			oled.showPageAt(row=row+2, col=11, data=heartInts)
			
			oled.showTextAt(row=row+3, align="center",  string="The Look")
			oled.showPageAt(row=row+3, col=0,  data=heartInts)
			oled.showPageAt(row=row+3, col=11, data=heartInts)
			
			oled.showPageAt(row=row+4, col=0,  data=heartInts)
			oled.showPageAt(row=row+4, col=11, data=heartInts)
			
			for i in xrange(12): # fill row
				oled.showPageAt(row=row+5, col=i, data=heartBytes)
				
			time.sleep(2)
			
			oled.clearDisplay()
			time.sleep(1)
			
			# image screen fade in
			for i in xrange(16):
				oled.setBrightness(i)
				oled.fillScreen(file="bacall.bin")
				time.sleep(0.16)
				
			oled.setBrightness(14)
			
			oled.fillScreen(file="bacall.bin")
			time.sleep(3)
			
			# add scroll text on top
			oled.setScroll(speed=2, endRow=0, endCol=11)
			oled.showTextAt(string="Glamour Star")
			time.sleep(0.5)
			oled.activeScroll()
			time.sleep(5)
			oled.desactiveScroll()
			
			oled.fillScreen(file="bacall.bin")
			
			oled.setScroll(to="left", speed=2, startRow=11, endRow=11, endCol=11)	
			oled.showTextAt(string="L.Bacall", row=11, align="right")
			time.sleep(2)
			oled.activeScroll()
			time.sleep(3)
			oled.desactiveScroll()
			
			oled.inverseDisplay()
			
			oled.fillScreen(file="bacall.bin")
			
			oled.setScroll(speed=25, endRow=0, endCol=11)	
			oled.showTextAt(string="The Look")
			time.sleep(2)
			oled.activeScroll()
			time.sleep(5)
			oled.desactiveScroll()
			
			oled.fillScreen(file="bacall.bin")
			
			oled.setScroll(to="left", speed=25, startRow=11 , endRow=11, endCol=11)	
			oled.showTextAt(string="of Hollywood", row=11, align="right")
			time.sleep(2)
			oled.activeScroll()
			time.sleep(5)
			oled.desactiveScroll()
			
			oled.normalDisplay()
			
			oled.fillScreen(file="bacall.bin")
			
			for i in [2,3,4,5,25,64]:
				oled.setScroll(speed=i)		
				oled.activeScroll()
				time.sleep(1)
				oled.desactiveScroll()
	except KeyboardInterrupt:
		oled.desactiveScroll()
		oled.normalDisplay()
		oled.clearDisplay()
		print "exit"
