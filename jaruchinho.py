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
from ps3 import *		#Import the PS3 library
from gopigo import *	#Import the GoPiGo library
# import picamera

print "Initializing"
p=ps3()		#Create a PS3 object
print "Done"

# camera = picamera.PiCamera()
# camera.vflip = True

s=80	#Initialize
imgid=0
while True:
	set_speed(s)	#Update the speed
	p.update()			#Read the ps3 values
	if p.up:			#If UP is pressed move forward
		fwd()
	elif p.left:		#If LEFT is pressed turn left
		left()
	elif p.right:		#If RIGHT is pressed move right
		right()
	elif p.down:		#If DOWN is pressed go back
		bwd()
	elif p.cross:		#If CROSS is pressed stop
		stop()
	elif p.circle:
		led_on(LED_L)
		led_on(LED_R)
	elif p.square:
		# camera.capture('image'+str(index)+'.jpg')
		index += 1
	else:
		stop()
		led_off(LED_L)
		led_off(LED_R)
	if p.l2:			#Increase the speed if L2 is pressed
		print s
		s+=2
		if s>255:
			s=255
	if p.r2:			#Decrease the speed if R2 is pressed
		print s
		s-=2
		if s<0:
			s=0
	x=(p.a_joystick_left_x+1)*90
	print int(x)
	if run:
		servo(int(x))	#Turn servo a/c to left joy movement
	time.sleep(.01)
