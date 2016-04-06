import io
import numpy
import os
import picamera
import time
from gopigo import *  # Import the GoPiGo library
from PIL import Image
import model

# Return CPU temperature as a character string
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return RAM information (unit=kb) in a list
# Index 0: total RAM
# Index 1: used RAM
# Index 2: free RAM
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

# Return % of CPU used by user as a character string
def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

# Return information about disk space as a list (unit included)
# Index 0: total disk space
# Index 1: used disk space
# Index 2: remaining disk space
# Index 3: percentage of disk used
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])

print "Starting..."
camera = picamera.PiCamera()
# camera.vflip = True
# camera.hflip = True
camera.resolution = (320, 240)
# camera.start_preview()

# camera.shutter_speed = 30000
# camera.framerate = 30

# wait for the camera adjust the gain
print "Warming up camera"
time.sleep(2)

print "Starting the motors"
set_speed(60)
# enable_com_timeout(1000)
# Little step to indicate that the script has started
enable_encoders()
enc_tgt(1,1,1)
fwd()

print "Initializing inference"
inference = model.inference()

while True:
    command = ''

    print "Distance"
    start = time.time()
    # distance = us_dist(15)
    distance = 100
    distance_elapsed = time.time() - start

    print "Camera"
    start = time.time()
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', resize=(160, 120), use_video_port=True) # change to 'yuv' later
    camera_elapsed = time.time() - start

    # RAM_stats = getRAMinfo()
    # RAM_total = round(int(RAM_stats[0]) / 1000,1)
    # RAM_used = round(int(RAM_stats[1]) / 1000,1)
    # RAM_free = round(int(RAM_stats[2]) / 1000,1)
    # print "Total: "+str(RAM_total)+"\tUsed: "+str(RAM_used)+"\tFree: "+str(RAM_free)

    print "Image data"
    start = time.time()
    stream.seek(0)
    image = Image.open(stream)
    image = image.convert('L') #makes it greyscale
    image_data = numpy.array(image)
    image_data = image_data.reshape(1, 19200)
    image_elapsed = time.time() - start

    print "Inference"
    start = time.time()
    command = inference.direction(image_data)
    inference_elapsed = time.time() - start

    # virtual bumper - prevents from moving fwd, left or right
    if distance <= 5 and not command == 'b':
        print "Bump!"
        command = 's'

    print(command+"\tdistance: "+str(distance_elapsed)+"\tcamera: "+str(camera_elapsed)+"\timage: "+str(image_elapsed)+"\tinference: "+str(inference_elapsed))

    print "Command"
    if command == 'f':
        fwd()
    elif command == 'r':
        right()
    elif command == 'l':
        left()
    elif command == 'b':
        bwd()
    elif command == 's':
        stop()
    else:
        stop()