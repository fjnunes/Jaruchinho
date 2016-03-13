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
        camera.framerate = 24
        camera.annotate_background = picamera.Color('black')
        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        start = dt.datetime.now()
        while (dt.datetime.now() - start).seconds < 30:
            camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            camera.wait_recording(0.2)
        # Start a preview and let the camera warm up for 2 seconds
        # camera.start_preview()
        # time.sleep(2)
        # Start recording, sending the output to the connection for 60
        # seconds, then stop
        camera.start_recording(connection, format='h264')
        # camera.wait_recording(60)
        # camera.stop_recording()
        input("Recording...")
finally:
    connection.close()
    client_socket.close()