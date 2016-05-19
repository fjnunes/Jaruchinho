import tensorflow as tf
import glob
import hashlib
import os.path
import re
import numpy
from PIL import Image

from tensorflow.python.platform import gfile

class DataSet(object):

  def __init__(self, images, labels, fake_data=False, one_hot=False,
               dtype=tf.float32):
    """Construct a DataSet.
    one_hot arg is used only if fake_data is true.  `dtype` can be either
    `uint8` to leave the input as `[0, 255]`, or `float32` to rescale into
    `[0, 1]`.
    """
    dtype = tf.as_dtype(dtype).base_dtype
    if dtype not in (tf.uint8, tf.float32):
      raise TypeError('Invalid image dtype %r, expected uint8 or float32' %
                      dtype)
    if fake_data:
      self._num_examples = 10000
      self.one_hot = one_hot
    else:
      assert images.shape[0] == labels.shape[0], (
          'images.shape: %s labels.shape: %s' % (images.shape,
                                                 labels.shape))
      self._num_examples = images.shape[0]

      # Convert shape from [num examples, rows, columns, depth]
      # to [num examples, rows*columns] (assuming depth == 1)
      # assert images.shape[3] == 1
      images = images.reshape(images.shape[0],
                              images.shape[1] * images.shape[2])
      if dtype == tf.float32:
        # Convert from [0, 255] -> [0.0, 1.0].
        images = images.astype(numpy.float32)
        images = numpy.multiply(images, 1.0 / 255.0)
    self._images = images
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0

  @property
  def images(self):
    return self._images

  @property
  def labels(self):
    return self._labels

  @property
  def num_examples(self):
    return self._num_examples

  @property
  def epochs_completed(self):
    return self._epochs_completed

  def next_batch(self, batch_size, fake_data=False):
    """Return the next `batch_size` examples from this data set."""
    if fake_data:
      fake_image = [1] * 784
      if self.one_hot:
        fake_label = [1] + [0] * 9
      else:
        fake_label = 0
      return [fake_image for _ in xrange(batch_size)], [
          fake_label for _ in xrange(batch_size)]
    start = self._index_in_epoch
    self._index_in_epoch += batch_size
    if self._index_in_epoch > self._num_examples:
      # Finished epoch
      self._epochs_completed += 1
      # Shuffle the data
      perm = numpy.arange(self._num_examples)
      numpy.random.shuffle(perm)
      self._images = self._images[perm]
      self._labels = self._labels[perm]
      # Start next epoch
      start = 0
      self._index_in_epoch = batch_size
      assert batch_size <= self._num_examples
    end = self._index_in_epoch
    return self._images[start:end], self._labels[start:end]

def _read32(bytestream):
  dt = numpy.dtype(numpy.uint32).newbyteorder('>')
  return numpy.frombuffer(bytestream.read(4), dtype=dt)[0]

def extract_image(filename):
  # image_data = gfile.FastGFile(filename, 'rb').read()
  image = Image.open(filename)
  image.thumbnail((160, 120), Image.ANTIALIAS)
  image = image.convert('L') #makes it greyscale
  data = numpy.array(image)
  data = data.reshape(1, 160*120)

  return data

def create_image_lists(image_dir, testing_percentage, validation_percentage):
  """Builds a list of training images from the file system.

  Analyzes the sub folders in the image directory, splits them into stable
  training, testing, and validation sets, and returns a data structure
  describing the lists of images for each label and their paths.

  Args:
    image_dir: String path to a folder containing subfolders of images.
    testing_percentage: Integer percentage of the images to reserve for tests.
    validation_percentage: Integer percentage of images reserved for validation.

  Returns:
    A dictionary containing an entry for each label subfolder, with images split
    into training, testing, and validation sets within each label.
  """
  if not gfile.Exists(image_dir):
    print("Image directory '" + image_dir + "' not found.")
    return None
  result = {}
  training_images = []
  training_labels = []
  testing_images = []
  testing_labels = []
  validation_images = []
  validation_labels = []

  file_list = []
  dir_name = os.path.basename(image_dir)
  file_glob = os.path.join(image_dir, '*.jpg')
  file_list.extend(glob.glob(file_glob))
  for file_name in file_list:
    base_name = os.path.basename(file_name)
    steering = float(re.search("(\d+)[^_]", base_name).group(0))
    label = (steering - 1552)/(1979-980)

    # We want to ignore anything after '_nohash_' in the file name when
    # deciding which set to put an image in, the data set creator has a way of
    # grouping photos that are close variations of each other. For example
    # this is used in the plant disease data set to group multiple pictures of
    # the same leaf.
    hash_name = re.sub(r'_nohash_.*$', '', file_name)
    # This looks a bit magical, but we need to decide whether this file should
    # go into the training, testing, or validation sets, and we want to keep
    # existing files in the same set even if more files are subsequently
    # added.
    # To do that, we need a stable way of deciding based on just the file name
    # itself, so we do a hash of that and then use that to generate a
    # probability value that we use to assign it.
    percentage_hash = (int(
        hashlib.sha1(hash_name).hexdigest(), 16) % (65536)) * (100 / 65535.0)
    if percentage_hash < validation_percentage:
      validation_images.append(extract_image(file_name))
      validation_labels.append(label)
    elif percentage_hash < (testing_percentage + validation_percentage):
      testing_images.append(extract_image(file_name))
      testing_labels.append(label)
    else:
      training_images.append(extract_image(file_name))
      training_labels.append(label)

    # result[label_name] = {
    #     'dir': dir_name,
    #     'training': training_images,
    #     'testing': testing_images,
    #     'validation': validation_images,
    # }
  # return result
  class DataSets(object):
    pass
  data_sets = DataSets()
  dtype=tf.float32
  data_sets.train = DataSet(numpy.array(training_images), numpy.array(training_labels), dtype=dtype)
  data_sets.validation = DataSet(numpy.array(validation_images), numpy.array(validation_labels), dtype=dtype)
  data_sets.test = DataSet(numpy.array(testing_images), numpy.array(testing_labels), dtype=dtype)

  return data_sets