import socket
import time
import picamera
import datetime as dt
from ps3 import *  # Import the PS3 library
from gopigo import *  # Import the GoPiGo library

jaruchinho_socket = socket.socket()
jaruchinho_socket.bind(('0.0.0.0', 8001))
jaruchinho_socket.listen(0)

camera_socket = socket.socket()
camera_socket.connect(('FernandoMacBookPro.local', 8000))

jaruchinho_connection = jaruchinho_socket.accept()[0].makefile('rb')
# Make a file-like object out of the connection
camera_connection = camera_socket.makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.vflip = True
        camera.hflip = True
        camera.resolution = (320, 240)
        camera.framerate = 10
        # camera.annotate_text = "Teste"
        camera.start_recording(camera_connection, format='mjpeg')

        while True:
            command=jaruchinho_connection.read(1)
            if command == 'f':
                fwd()
            elif command == 'l':
                left()
            elif command == 'r':
                right()
            else:
                stop()

finally:
    camera_connection.close()
    camera_socket.close()