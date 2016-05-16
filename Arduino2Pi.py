import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
# ser = serial.Serial('/dev/tty.usbmodemFD141', 115200, timeout=1)
while True:

    ser.write("s1200\n")
    response = ser.readline()
    if response != "OK\r\n":
        print "Took over S"


    ser.write("t1650\n")
    response = ser.readline()
    if response != "OK\r\n":
        print "Took over throtle"

    time.sleep(0.1)
