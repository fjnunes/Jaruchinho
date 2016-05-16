import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
# ser = serial.Serial('/dev/tty.usbmodemFD141', 115200, timeout=1)
while True:
    servoVal = "s1200\r\n"
    throtleVal = "t1650\r\n"

    ser.write(servoVal)
    servo = ser.readline()
    if (servo != servoVal):
        print "Took over servo"

    # ser.write(throtleVal)
    # throtle = ser.readline()
    # if (servo != servoVal):
    #     print "Took over throtle"

    time.sleep(0.1)
