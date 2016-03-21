import socket
import cv2
import numpy as np
import tensorflow as tf
import os.path
import inference

from tensorflow.python.platform import gfile

def create_graph():
  """Creates a graph from saved GraphDef file and returns a saver."""
  # Creates graph from saved graph_def.pb.
  with tf.gfile.FastGFile(os.path.join("./", 'output_graph.pb'), 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

connected = False
jaruchinho_socket = socket.socket()

camera_socket = socket.socket()
camera_socket.bind(('0.0.0.0', 8000))
camera_socket.listen(0)

# Accept a single connection and make a file-like object out of it
camera_connection = camera_socket.accept()[0].makefile('rb')

inf = inference.inference()

i = 0
f = 'r'
try:
    bytes=''
    while True:
        bytes+=camera_connection.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
            cv2.imwrite("/tmp/img.jpg", image);
            cv2.imshow('image',image)

            if not connected:
                jaruchinho_socket.connect(('dex.local', 8008))
                connected = True

            image_data = gfile.FastGFile("/tmp/img.jpg", 'r').read()
            image_data = image_data.convert('L')
            direction = inf.direction(image_data)
            print(direction)

            jaruchinho_socket.send(direction)

            if cv2.waitKey(1) == 27:
                exit(0)
finally:
    camera_connection.close()
    camera_socket.close()