#!/usr/bin/env python
import smbus, time, textwrap
import numpy as np

NAME = "Rgb Lcd i2c class"
VERSION = "0.0.1"
DATE = "2018 June 14"
AUTHOR = "Andres Lozano a.k.a Loz"
COPYRIGHT = "Copyleft: This is a free work, you can copy, distribute, and modify it under the terms of the Free Art License http://artlibre.org/licence/lal/en/"
URL = "http://hyperficiel.com"
DESCRIPTION = "class to use rgb seeedstudio lcd display https://www.seeedstudio.com/Grove-self.LCD_-RGB-Backlight-p-1643.html "

class RgbLcd:
	def __init__(self, bus=None):
		# this device has two I2C addresses
		self.LCD_RGB_ADRESS = 0x62
		self.LCD_TEXT_ADRESS = 0x3e

		# commands
		self.LCD_COMMAND_MODE = 0x80
		self.LCD_TEXT_MODE = 0x40

		self.LCD_CLEAR_DISPLAY = 0x01
		self.LCD_RETURN_HOME = 0x02
		self.LCD_ENTRY_MODE_SET = 0x04
		self.LCD_DISPLAY_CONTROL = 0x08
		self.LCD_CURSOR_SHIFT = 0x10
		self.LCD_FUNCTION_SET = 0x20

		# flags for display entry mode
		self.LCD_ENTRY_RIGHT = 0x00
		self.LCD_ENTRY_LEFT = 0x02
		self.LCD_ENTRY_SHIFT_INCREMENT = 0x01
		self.LCD_ENTRY_SHIFT_DECREMENT = 0x00

		# flags for display on/off control
		self.LCD_DISPLAY_ON = 0x04
		self.LCD_DISPLAY_OFF = 0x00
		self.LCD_CURSOR_ON = 0x02
		self.LCD_CURSOR_OFF = 0x00
		self.LCD_BLINK_ON = 0x01
		self.LCD_BLINK_OFF = 0x00

		# flags for display/cursor shift
		self.LCD_DISPLAY_MOVE = 0x08
		self.LCD_CURSOR_MOVE = 0x00
		self.LCD_MOVE_RIGHT = 0x04
		self.LCD_MOVE_LEFT = 0x00

		# flags for function set
		self.LCD_8BIT_MODE = 0x10
		self.LCD_4BIT_MODE = 0x00
		self.LCD_2LINE = 0x08
		self.LCD_1LINE = 0x00
		self.LCD_5X10DOTS = 0x04
		self.LCD_5X8DOTS = 0x00

		self.bus = bus
		self.delay = 0.050 # millis
		
		self.writeCommand(0x28) # 2 lines
		self.writeCommand(0x08 | 0x04) # display on, no cursor
		self.display()
		self.clear()
		self.home()
		self.backlight()
		
	# Clear screen
	def clear(self):
		self.writeCommand(self.LCD_CLEAR_DISPLAY)
		
	# Return to home(top-left corner of self.LCD_)
	def home(self):
		self.writeCommand(self.LCD_RETURN_HOME)
		time.sleep(self.delay * 10) # this command takes a long time!

	# set backlight to (R,G,B) (values from 0..255 for each)
	def setRGB(self, rgb=(0,0,0)):
		self.bus.write_byte_data(self.LCD_RGB_ADRESS,0,0)
		self.bus.write_byte_data(self.LCD_RGB_ADRESS,1,0)
		self.bus.write_byte_data(self.LCD_RGB_ADRESS,0x08,0xaa)
		self.bus.write_byte_data(self.LCD_RGB_ADRESS,4,rgb[0])
		self.bus.write_byte_data(self.LCD_RGB_ADRESS,3,rgb[1])
		self.bus.write_byte_data(self.LCD_RGB_ADRESS,2,rgb[2])

	# send command to display (no need for external use)    
	def writeCommand(self, cmd=None):
		self.bus.write_byte_data(self.LCD_TEXT_ADRESS, self.LCD_COMMAND_MODE, cmd)
		time.sleep(self.delay)

	def setCursor(self, row=0, col=0):
		if row == 0:
			col = col | 0x80
		else:
			col = col | 0xc0
			
		self.writeCommand(col)
		
	# Pause lcd
	def pause(self, delay=1):
		time.sleep(delay)
		
	# Turn the display on/off (quickly)
	def noDisplay(self):
		self.writeCommand(self.LCD_DISPLAY_CONTROL | self.LCD_DISPLAY_OFF)

	def display(self):
		self.writeCommand(self.LCD_DISPLAY_CONTROL | self.LCD_DISPLAY_ON)

	# Turns the underline cursor on/off
	def noCursor(self):
		self.writeCommand(self.LCD_DISPLAY_CONTROL | self.LCD_CURSOR_OFF)

	def cursor(self): 
		self.writeCommand(self.LCD_DISPLAY_CONTROL | self.LCD_CURSOR_ON)

	# Turn on and off the blinking cursor
	def noBlink(self):
		self.writeCommand(self.LCD_DISPLAY_CONTROL | self.LCD_BLINK_OFF)

	def blink(self):
		self.writeCommand(self.LCD_DISPLAY_CONTROL | self.LCD_BLINK_ON)

	# These commands scroll the display without changing the RAM
	def scrollDisplayLeft(self, times=1, speed=0.05):
		for i in xrange(times):
			self.writeCommand(self.LCD_CURSOR_SHIFT | self.LCD_DISPLAY_MOVE | self.LCD_MOVE_LEFT)
			lcd.pause(speed)
			

	def scrollDisplayRight(self, times=1, speed=0.05):
		for i in xrange(times):
			self.writeCommand(self.LCD_CURSOR_SHIFT | self.LCD_DISPLAY_MOVE | self.LCD_MOVE_RIGHT)
			lcd.pause(speed)

	# This is for text that flows Left to Right
	def leftToRight(self):
		self.writeCommand(self.LCD_ENTRY_MODE_SET | self.LCD_ENTRY_LEFT)

	# This is for text that flows Right to Left
	def rightToLeft(self):
		self.writeCommand(self.LCD_ENTRY_MODE_SET | self.LCD_ENTRY_RIGHT)

	# This will 'right justify' text from the cursor
	def autoscroll(self):
		self.writeCommand(self.LCD_ENTRY_MODE_SET | self.LCD_ENTRY_SHIFT_INCREMENT)

	# This will 'left justify' text from the cursor
	def noAutoscroll(self):
		self.writeCommand(self.LCD_ENTRY_MODE_SET | self.LCD_ENTRY_SHIFT_DECREMENT)
	
	# Turn off the backlight
	def noBacklight(self):
		self.setRGB()
		
	# Turn on the back light
	def backlight(self):
		self.setRGB(rgb=(0,64,0)) # few green
		
	def showSpecialChars(self, chars=[0]):
		# the chars value can be a single or multiple (array) char location
		if type(chars).__name__ == "int": 
			# single char
			chars = [chars]
			
		if max(chars) > 7:
			print "chars out of range"
			return
			
		self.bus.write_i2c_block_data(self.LCD_TEXT_ADRESS, self.LCD_TEXT_MODE, chars)
			
	# Print text/string into screen only ascii characters
	def showText(self, text="", align=0):
		if align:text = self.alignText(text, align)
		data = map(ord, text)	
		self.bus.write_i2c_block_data(self.LCD_TEXT_ADRESS, self.LCD_TEXT_MODE, data)
			
	# Typewriter style	
	def typeWriter(self, text="", delay=0.1, align=0):
		if align:text = self.alignText(text, align)
		for c in text:
			self.bus.write_byte_data(self.LCD_TEXT_ADRESS, self.LCD_TEXT_MODE, ord(c))
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

	# Create a custom character (from array of row patterns)
	def createChar(self, location=0, pattern=None):
		if len(pattern) == 40:pattern = self.getChar(data=pattern)
		location &= 0x07 # Make sure location is 0-7
		self.writeCommand(self.LCD_TEXT_MODE | (location << 3))
		self.bus.write_i2c_block_data(self.LCD_TEXT_ADRESS, self.LCD_TEXT_MODE, pattern)
		
	def getChar(self, data=None):
		"""return array of 8 bytes"""
		arr = []
		data = np.array(data)
		data = data.reshape(8, 5, order="C")
		for byte in data:
			arr.append(255 ^ eval("0b"+"".join([str(bit) for bit in byte])))
		
		# return a list of 8 bytes	
		return arr

# example code
if __name__=="__main__":
	print "you are in class RgbLcd"
	
	delay = 1
	
	bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
	lcd = RgbLcd(bus)
	lcd.clear()
	
	try:
		toi_mon_toi = [
			"Prends un petit poisson",
			"Glisse-le entre mes jambes",
			"Il n'y a pas de raison",
			"Pour se tirer la langue"
		]
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
			
			# specials chars test
			specialChar = [ # char description every "0" = black pixel
				0, 0, 0, 0, 0,
				1, 0, 0, 0, 1,
				1, 1, 0, 1, 1,
				0, 1, 1, 0, 0,
				0, 1, 1, 0, 0,
				1, 1, 0, 1, 1,
				1, 0, 0, 0, 1,
				0, 0, 0, 0, 0,
			]
			# put special char in location 0 or index 0 of (0-7)
			lcd.createChar(location=0, pattern=specialChar)
			lcd.setCursor(row=0)
			# put 16 special chars of location 0
			lcd.showSpecialChars([0]*16)
			lcd.pause(delay)
			lcd.setCursor(row=1)
			lcd.showSpecialChars([0]*16)
			lcd.pause(delay*3)
			lcd.clear()
			
			lcd.noBacklight()
			print "end"
	except KeyboardInterrupt:
		lcd.clear()
		lcd.noBacklight()
		print "close device"
	
	

