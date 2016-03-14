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

set_speed(30)

try:
    with picamera.PiCamera() as camera:
        camera.vflip = True
        camera.hflip = True
        camera.resolution = (640, 480)
        camera.framerate = 2
        # camera.annotate_text = "Teste"
        camera.start_recording(camera_connection, format='mjpeg')

        if not connected:
            jaruchinho_connection = jaruchinho_socket.accept()[0].makefile('rb')
            connected = True

        while True:
            command = jaruchinho_connection.read(1)
            print(command)
            if command == 'f':
                fwd()
            elif command == 'r':
                right()
            elif command == 'l':
                left()
            else:
                stop()
                time.sleep(0.1)

finally:
    camera_connection.close()
    camera_socket.close()