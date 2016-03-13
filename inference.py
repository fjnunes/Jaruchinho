
import numpy as np
import tensorflow as tf
import os.path

from tensorflow.python.platform import gfile

image_data_tensor_name = 'DecodeJpeg/contents'
final_tensor_name = 'final_result'

def ensure_name_has_port(tensor_name):
  """Makes sure that there's a port number at the end of the tensor name.

  Args:
    tensor_name: A string representing the name of a tensor in a graph.

  Returns:
    The input string with a :0 appended if no port was specified.
  """
  if ':' not in tensor_name:
    name_with_port = tensor_name + ':0'
  else:
    name_with_port = tensor_name
  return name_with_port

def create_graph():
    """Creates a graph from saved GraphDef file and returns a saver."""
    # Creates graph from saved graph_def.pb.
    with tf.Session() as sess:
        with tf.gfile.FastGFile(os.path.join("/tmp/", 'output_graph.pb'), 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')
    return sess.graph

graph = create_graph()
sess = tf.Session()

# Set up all our weights to their initial default values.
init = tf.initialize_all_variables()
sess.run(init)

result = ""
while True:
    image_path = raw_input('Image path: ')
    image_data = gfile.FastGFile("/Users/jaruche/Desktop/JImages/images/"+str(image_path), 'r').read()

    result = sess.run(
      ensure_name_has_port(final_tensor_name),
      { ensure_name_has_port(image_data_tensor_name): image_data })

    i = 0
