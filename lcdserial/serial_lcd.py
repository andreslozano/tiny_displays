#! /usr/bin/env python
#-*- coding: utf-8 -*-

import time, serial, os, textwrap

# Au-dessus de Paris
# la lune est violette.
# Elle devient jaune
# dans les villes mortes.

NAME = "Serial Lcd"
VERSION = "0.0.2"
DATE = "2018 April 26"
AUTHOR = "Andres Lozano a.k.a Loz"
COPYRIGHT = "Copyleft: This is a free work, you can copy, distribute, and modify it under the terms of the Free Art License http://artlibre.org/licence/lal/en/"
URL = "http://hyperficiel.com"
DESCRIPTION = "Seeedstudio grove serial lcd https://www.seeedstudio.com/Grove-Serial-LCD-p-773.html"

class SerialLCD:
	def __init__(self, port=None, speed=9600):
		"""
		list ports aviaibles (linux):
		$ dmesg | grep tty
		list ports aviaibles (windows):
		$ python -m serial.tools.list_ports
		"""
		# Initialization Commands or Responses
		self.SLCD_INIT = 0xA3
		self.SLCD_INIT_ACK = 0xA5
		self.SLCD_INIT_DONE = 0xAA

		# WorkingMode Commands or Responses
		self.SLCD_CONTROL_HEADER = 0x9F
		self.SLCD_CHAR_HEADER = 0xFE
		self.SLCD_CURSOR_HEADER = 0xFF
		self.SLCD_CURSOR_ACK = 0x5A

		self.SLCD_RETURN_HOME = 0x61
		self.SLCD_DISPLAY_OFF = 0x63
		self.SLCD_DISPLAY_ON = 0x64
		self.SLCD_CLEAR_DISPLAY = 0x65
		self.SLCD_CURSOR_OFF = 0x66
		self.SLCD_CURSOR_ON = 0x67
		self.SLCD_BLINK_OFF = 0x68
		self.SLCD_BLINK_ON = 0x69
		self.SLCD_SCROLL_LEFT = 0x6C
		self.SLCD_SCROLL_RIGHT = 0x72
		self.SLCD_NO_AUTO_SCROLL = 0x6A
		self.SLCD_AUTO_SCROLL = 0x6D
		self.SLCD_LEFT_TO_RIGHT = 0x70
		self.SLCD_RIGHT_TO_LEFT = 0x71
		self.SLCD_POWER_ON = 0x83
		self.SLCD_POWER_OFF = 0x82
		self.SLCD_INVALIDCOMMAND = 0x46
		self.SLCD_BACKLIGHT_ON = 0x81
		self.SLCD_BACKLIGHT_OFF = 0x80

		con, self.device = self.openPort(port=port, speed=speed)
		
		# show infos
		# print "Open",self.device.is_open,"port",con,"speed",speed
		print self.device
		
		self.delay = 0.01 # 10 millis
		self.write(self.SLCD_CONTROL_HEADER)	
		self.write(self.SLCD_POWER_OFF) 
		self.write(self.SLCD_CONTROL_HEADER)	
		self.write(self.SLCD_POWER_ON)
		self.write(self.SLCD_INIT_ACK)
		while True:
			r = self.device.read(1)
			if r and ord(r) == self.SLCD_INIT_DONE:
				break
		
	# Sub function here to write data to serial
	def write(self, data=None):
		try:
			if type(data).__name__ == "int":
				self.device.write(chr(data))
			elif type(data).__name__ == "str":
				self.device.write(data)
			else:
				print "no value wrote to device!"
		except:
			print "error write device"
			exit("error write device")
			
		time.sleep(self.delay) # wait transmission done
			
	# Print text/string into screen only ascii characters
	def showText(self, text="", align=0):
		if align:text = self.alignText(text, align)
		self.write(self.SLCD_CHAR_HEADER)
		self.write(text)
		
	# Typewriter style	
	def typeWriter(self, text="", delay=0.1, align=0):
		if align:text = self.alignText(text, align)
		self.write(self.SLCD_CHAR_HEADER)
		for c in text:
			self.write(c)
			time.sleep(delay)
			
	# Align text
	def alignText(self, text="", align=0):
		# align 0 = nothing, text at cursor
		# align 1 = centered text and fill line
		# align 2 = right and fill line
		# align 3 = left and fill line
		if align == 1: 
			f = "{:^"+str(16)+"}"
			return f.format(text)
		elif align == 2:
			f = "{:>"+str(16)+"}"
			return f.format(text)
		elif align == 3:
			f = "{:"+str(16)+"}"
			return f.format(text)
		else:
			return text
			
	# Clear screen
	def clear(self):
		self.write(self.SLCD_CONTROL_HEADER)	
		self.write(self.SLCD_CLEAR_DISPLAY)	

	# Return to home(top-left corner of LCD)
	def home(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_RETURN_HOME)  
		time.sleep(self.delay * 2) # this command needs more time 
		
	# Reset clear & home
	def clearHome(self):
		self.clear()
		self.home()
	
	# Pause lcd
	def pause(self, delay=1):
		time.sleep(delay)

	# Set Cursor to (Column,Row) Position
	def setCursor(self, row=0, col=0):
		self.write(self.SLCD_CONTROL_HEADER) 
		self.write(self.SLCD_CURSOR_HEADER) #cursor header command
		self.write(col)
		self.write(row)

	# Switch the display off without clearing RAM
	def noDisplay(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_DISPLAY_OFF)	 

	# Switch the display on
	def display(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_DISPLAY_ON)	 

	# Switch the underline cursor off
	def noCursor(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_CURSOR_OFF)	  

	# Switch the underline cursor on
	def cursor(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_CURSOR_ON)	  

	# Switch off the blinking cursor
	def noBlink(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_BLINK_OFF)	  

	# Switch on the blinking cursor
	def blink(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_BLINK_ON)	  

	# Scroll the display left without changing the RAM
	def scrollDisplayLeft(self, times=1, speed=0.05):
		for i in xrange(times):
			self.write(self.SLCD_CONTROL_HEADER)
			self.write(self.SLCD_SCROLL_LEFT)
			lcd.pause(speed)
		

	# Scroll the display right without changing the RAM
	def scrollDisplayRight(self, times=1, speed=0.05):
		for i in xrange(times):
			self.write(self.SLCD_CONTROL_HEADER)
			self.write(self.SLCD_SCROLL_RIGHT)
			lcd.pause(speed)

	# Set the text flow "Left to Right"
	def leftToRight(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_LEFT_TO_RIGHT)

	# Set the text flow "Right to Left"
	def rightToLeft(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_RIGHT_TO_LEFT)

	# This will 'right justify' text from the cursor
	def autoScroll(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_AUTO_SCROLL)

	# This will 'left justify' text from the cursor
	def noAutoScroll(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_NO_AUTO_SCROLL)
		
	# SLCD power on
	def power(self):
		self.write(self.SLCD_CONTROL_HEADER)	
		self.write(self.SLCD_POWER_ON)
		
	# SLCD power off
	def noPower(self):
		self.write(self.SLCD_CONTROL_HEADER)	
		self.write(self.SLCD_POWER_OFF)

	# Turn off the backlight
	def noBacklight(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_BACKLIGHT_OFF)
		
	# Turn on the back light
	def backlight(self):
		self.write(self.SLCD_CONTROL_HEADER)
		self.write(self.SLCD_BACKLIGHT_ON)
			
	# Search and find auto tty/com port if only one port is alive
	def openPort(self, port=None, speed=9600):
		# different ways to connect serial	
		def connectMsWindows(port=None, speed=9600):
			try:
				device = serial.Serial()
				device.baudrate = speed
				device.setPort(port)
				device.open()
				return 1, device
			except:
				return 0, None

		def connectPosix(port=None, speed=9600):
			try:
				device = serial.Serial(port, speed)
				return 1, device
			except: 
				return 0, None
				
		"""search port aviaible on both window and linux"""
		maxPorts = 100
		found = 0
		if os.name == "nt":
			if port and not port in ["COM1","COM64"]:
				found, device = connectMsWindows(port=port, speed=speed)
			else:
				i = 0
				while i < maxPorts:
					port = "COM%d" % (i,)
					if not i in [1,64]: # COM1 and COM64 always reserved in windows 
						found, device = connectMsWindows(port=port, speed=speed)
						if found:break
					i += 1
					
			if found == 0: exit("no nt serial device found")
			return port, device
		elif os.name == "posix":
			if port:
				found, device = connectPosix(port=port, speed=speed)
			else:
				i = 0
				while i < maxPorts:
					# port = "/dev/ttyACM%d" % (i,)
					port = "/dev/ttyUSB%d" % (i,)
					found, device = connectPosix(port=port, speed=speed)
					if found:break
					i += 1
					
			if found == 0: exit("no posix serial device found")
			return port, device
		else:
			exit("no 'nt' or 'posix' serial device found")

if __name__ == "__main__":
	print "you are in class SerialLCD"
	toi_mon_toi = [
		"Prends un petit poisson",
		"Glisse-le entre mes jambes",
		"Il n'y a pas de raison",
		"Pour se tirer la langue",
		"Ne me regarde pas",
		"Comme ca tout de travers",
		"Qui fait le premier pas",
		"Pour s'aimer a l'envers"
	]
	lcd = SerialLCD()
	delay = 2
	try:
		while True:
			lcd.backlight()
			for line in toi_mon_toi:
				line = line.upper()
				row = 1
				lcd.pause(delay)
				for words in textwrap.wrap(line, 16): # 16 max chars by line
					row = row ^ 1 # switch to next line
					if row == 0:
						lcd.clear()
						lcd.home()
						lcd.showText(words)
						print "row", row, words
						lcd.pause(delay)
					else:
						lcd.setCursor(row=row, col=0)
						lcd.showText(words)
						print "row", row, words
						lcd.pause(delay)
						lcd.scrollDisplayRight(times=16)
			
			time.sleep(delay)
			lcd.clear()
			lcd.noBacklight()
			lcd.pause(1)
			print "end"
	except KeyboardInterrupt:
		lcd.clear()
		lcd.noBacklight()
		lcd.device.close()
		print "close device"
		
	
