import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
# ser = serial.Serial('/dev/tty.usbmodemFD141', 115200, timeout=1)
while True:

    tookover = False
    ser.write("s1200\n")
    response = ser.readline()
    if response != "OK\r\n":
        tookover = True

    ser.write("t1650\n")
    response = ser.readline()
    if (response != "OK\r\n" or tookover) and int(response) < 1650-20 :
        print "Took over"

    time.sleep(0.1)
