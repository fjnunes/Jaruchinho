import socket
import time
import picamera
import datetime as dt

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket()
client_socket.connect(('FernandoiMac.local', 6000))

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.vflip = True
        camera.hflip = True
        camera.resolution = (320, 240)
        camera.framerate = 10
        # camera.annotate_text = "Teste"
        camera.start_recording(connection, format='h264')

        input("Recording...")
finally:
    connection.close()
    client_socket.close()