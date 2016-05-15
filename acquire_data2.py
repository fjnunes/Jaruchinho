#!/usr/bin/env python
########################################################################
# This example controls the GoPiGo and using a PS3 Dualshock 3 controller
#
# http://www.dexterindustries.com/GoPiGo/
# History
# ------------------------------------------------
# Author     	Date      		Comments
# Karan Nayan   11 July 14		Initial Authoring
'''
## License
 GoPiGo for the Raspberry Pi: an open source robotics platform for the Raspberry Pi.
 Copyright (C) 2015  Dexter Industries

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
'''
#
# left,right,up,down to control
# cross to stop
# left joy to turn the camera servo
# l2 to increase speed
# r2 to decrease speed
########################################################################
import picamera
import serial
import time
import os

print "Initializing"
camera = picamera.PiCamera()
# camera.vflip = True
# camera.hflip = True
# camera.led = False
# camera.brightness = 60
camera.resolution = (320, 240)

# wait for the camera adjust the gain
print "Warming up camera"
time.sleep(2)

imgid = 0
recording = False

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

if not os.path.exists("images"):
	os.makedirs("images")

print "Capturing..."
while True:
	ser.write("T\n")
	throtle = int(serial.readline())
	if (throtle < 1486 + 20 and throtle < 1486 - 20):
		continue

	ser.write("S\n")
	steering = serial.readline()
	camera.capture('images/'+steering +'_'+ str(imgid) + '.jpg', use_video_port=True)

	imgid += 1
