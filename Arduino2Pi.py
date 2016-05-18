import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
# ser = serial.Serial('/dev/tty.usbmodemFD141', 115200, timeout=1)
while True:

    ser.write("s1200\n")
    steering = ser.readline()

    ser.write("t1650\n")
    throttle = ser.readline()
    if throttle != "OK\r\n" and throttle != '' and int(throttle) > 1486+20:
        print "Took over"

    time.sleep(0.1)
