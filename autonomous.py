import picamera
import datetime as dt
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
    command = ''
    distance = us_dist(15)

    stream = io.BytesIO()
    camera.capture_continuous(stream, 'jpeg', use_video_port=True)
    # camera.capture(stream, format='jpeg', resize=(160, 120))
    stream.seek(0)
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    image = Image.open(stream.read())
    stream.seek(0)
    stream.truncate()

    image = image.convert('L') #makes it greyscale
    image_data = numpy.array(image)
    image_data = image_data.reshape(1, 19200)

    command = inference.direction(image_data)

    # virtual bumper - prevents from moving fwd, left or right
    if distance <= 5 and not command == 'b':
        print "Bump!"
        command = 's'

    print(command)
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