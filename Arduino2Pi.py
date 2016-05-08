import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
# ser = serial.Serial('/dev/tty.usbmodemFD141', 115200, timeout=1)
while True:
    ser.write("s1200\n")
    ser.write("t1600\n")
    time.sleep(0.05)
