import picamera
import time
from gopigo import *  # Import the GoPiGo library
# import model
from PIL import Image, ImageFile
import io
import numpy


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
set_speed(50)
# enable_com_timeout(1000)
# Little step to indicate that the script has started
enable_encoders()
enc_tgt(1,1,1)
fwd()

print "Initializing inference"
# inference = model.inference()

while True:
    command = ''

    print "Distance"
    start = time.time()
    distance = us_dist(15)
    distance_elapsed = time.time() - start

    print "Camera"
    start = time.time()
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', resize=(160, 120), use_video_port=True) # change to 'yuv' later
    camera_elapsed = time.time() - start

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
    # command = inference.direction(image_data)
    command = 'f'
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