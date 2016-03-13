import socket
import subprocess
import cv2
import numpy as np

jaruchinho_socket = socket.socket()
jaruchinho_socket.connect(('dex.local', 8008))

camera_socket = socket.socket()
camera_socket.bind(('0.0.0.0', 8000))
camera_socket.listen(0)

# Accept a single connection and make a file-like object out of it
camera_connection = camera_socket.accept()[0].makefile('rb')
try:
    bytes=''
    while True:
        bytes+=camera_connection.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
            cv2.imshow('i',i)

            jaruchinho_socket.send("r")

            if cv2.waitKey(1) == 27:
                exit(0)
finally:
    camera_connection.close()
    camera_socket.close()