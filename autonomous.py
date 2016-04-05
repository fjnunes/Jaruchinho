import picamera
import time
from gopigo import *  # Import the GoPiGo library
import model
from PIL import Image, ImageFile
import io
import numpy

camera = picamera.PiCamera()
# camera.vflip = True
# camera.hflip = True
camera.resolution = (320, 240)
camera.framerate = 12

# wait for the camera adjust the gain
time.sleep(2)

set_speed(50)

enable_com_timeout(1000)
# Little step to indicate that the script has started
enable_encoders()
enc_tgt(1,1,1)
fwd()

inference = model.inference()

while True:
    start = time.time()
    command = ''
    distance = us_dist(15)
    done = time.time()
    distance_elapsed = done - start

    start = time.time()
    stream = io.BytesIO()
    camera.capture_continuous(stream, format='png', resize=(160, 120), use_video_port=True) # change to 'yuv' later
    done = time.time()
    camera_elapsed = done - start

    start = time.time()
    stream.seek(0)
    image = Image.open(stream)
    image = image.convert('L') #makes it greyscale
    image_data = numpy.array(image)
    image_data = image_data.reshape(1, 19200)
    done = time.time()
    image_elapsed = done - start

    start = time.time()
    command = inference.direction(image_data)
    done = time.time()
    inference_elapsed = done - start

    # virtual bumper - prevents from moving fwd, left or right
    if distance <= 5 and not command == 'b':
        print "Bump!"
        command = 's'

    print(command+"\tdistance: "+str(distance_elapsed)+"\tcamera: "+str(camera_elapsed)+"\timage: "+str(image_elapsed)+"\tinference: "+str(inference_elapsed))

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