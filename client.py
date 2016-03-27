import socket
import time
import picamera
import datetime as dt
from ps3 import *  # Import the PS3 library
from gopigo import *  # Import the GoPiGo library

connected = False
jaruchinho_socket = socket.socket()
jaruchinho_socket.bind(('0.0.0.0', 8008))
jaruchinho_socket.listen(0)

camera_socket = socket.socket()
camera_socket.connect(('FernandoMacBookPro.local', 8000))

# Make a file-like object out of the connection
camera_connection = camera_socket.makefile('wb')

set_speed(50)

p = ps3()  # Create a PS3 object
s = 80  # Initializ

# Little step to indicate that the script has started
enable_encoders()
enc_tgt(1,1,1)
fwd()

try:
    camera = picamera.PiCamera()
    # camera.vflip = True
    # camera.hflip = True
    camera.resolution = (640, 480)
    camera.framerate = 4
    camera.start_recording(camera_connection, format='mjpeg')

    while True:
        command = ''
        distance = us_dist(15)
        p.update()  # Read the ps3 values

        if p.up:  # If UP is pressed move forward
            command = 'f'
        elif p.left:  # If LEFT is pressed turn left
            command = 'l'
        elif p.right:  # If RIGHT is pressed move right
            command = 'r'
        elif p.down:  # If DOWN is pressed go back
            command = 'b'
        else:
            command = 's'

        if p.circle:
            led_on(LED_L)
            led_on(LED_R)
        else:
            # stop()
            led_off(LED_L)
            led_off(LED_R)

        if p.triangle:
            print "Distance: "+ distance

        if p.l2:
            if not connected:
                jaruchinho_connection = jaruchinho_socket.accept()[0].makefile('rb')
                connected = True
            command = jaruchinho_connection.read(1)

        if distance <= 5:
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
            time.sleep(1)

finally:
    camera_connection.close()
    camera_socket.close()