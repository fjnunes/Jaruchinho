from __future__ import division

import os.path
import time

import numpy
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf
import glob
import hashlib
import re

from tensorflow.python.platform import gfile
from tensorflow.python.client import graph_util

import regression
import regression_data

# Basic model parameters as external flags.
flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_float('learning_rate', 0.0001, 'Initial learning rate.')
flags.DEFINE_integer('max_steps', 2000, 'Number of steps to run trainer.')
flags.DEFINE_integer('hidden1', 128, 'Number of units in hidden layer 1.')
flags.DEFINE_integer('hidden2', 32, 'Number of units in hidden layer 2.')
flags.DEFINE_integer('batch_size', 256, 'Batch size.  '
                     'Must divide evenly into the dataset sizes.')
flags.DEFINE_string('train_dir', 'data', 'Directory to put the training data.')
flags.DEFINE_boolean('fake_data', False, 'If true, uses fake data '
                     'for unit testing.')

# Input and output file flags.
flags.DEFINE_string('image_dir', '../images',
                           """Path to folders of labeled images.""")
flags.DEFINE_string('output_graph', './output_graph.pb',
                           """Where to save the trained graph.""")
flags.DEFINE_string('output_labels', './output_labels.txt',
                           """Where to save the trained graph's labels.""")

# Details of the training configuration.
flags.DEFINE_integer(
    'testing_percentage', 10,
    """What percentage of images to use as a test set.""")
flags.DEFINE_integer(
    'validation_percentage', 10,
    """What percentage of images to use as a validation set.""")


def placeholder_inputs(batch_size, name=''):
  """Generate placeholder variables to represent the input tensors.
  These placeholders are used as inputs by the rest of the model building
  code and will be fed from the downloaded data in the .run() loop, below.
  Args:
    batch_size: The batch size will be baked into both placeholders.
  Returns:
    images_placeholder: Images placeholder.
    labels_placeholder: Labels placeholder.
  """
  # Note that the shapes of the placeholders match the shapes of the full
  # image and label tensors, except the first dimension is now batch_size
  # rather than the full size of the train or test data sets.
  images_placeholder = tf.placeholder(tf.float32, shape=(None,
                                                         regression.IMAGE_PIXELS), name=name)
  labels_placeholder = tf.placeholder(tf.float32, shape=(batch_size))
  return images_placeholder, labels_placeholder


def fill_feed_dict(data_set, images_pl, labels_pl):
  """Fills the feed_dict for training the given step.
  A feed_dict takes the form of:
  feed_dict = {
      <placeholder>: <tensor of values to be passed for placeholder>,
      ....
  }
  Args:
    data_set: The set of images and labels, from input_data.read_data_sets()
    images_pl: The images placeholder, from placeholder_inputs().
    labels_pl: The labels placeholder, from placeholder_inputs().
  Returns:
    feed_dict: The feed dictionary mapping from placeholders to values.
  """
  # Create the feed_dict for the placeholders filled with the next
  # `batch size ` examples.
  images_feed, labels_feed = data_set.next_batch(FLAGS.batch_size,
                                                 FLAGS.fake_data)
  feed_dict = {
      images_pl: images_feed,
      labels_pl: labels_feed,
  }
  return feed_dict


def do_eval(sess,
            eval_correct,
            images_placeholder,
            labels_placeholder,
            data_set):
  """Runs one evaluation against the full epoch of data.
  Args:
    sess: The session in which the model has been trained.
    eval_correct: The Tensor that returns the number of correct predictions.
    images_placeholder: The images placeholder.
    labels_placeholder: The labels placeholder.
    data_set: The set of images and labels to evaluate, from
      input_data.read_data_sets().
  """
  # And run one epoch of eval.
  true_count = 0  # Counts the number of correct predictions.
  steps_per_epoch = data_set.num_examples // FLAGS.batch_size
  num_examples = steps_per_epoch * FLAGS.batch_size
  for step in xrange(steps_per_epoch):
    feed_dict = fill_feed_dict(data_set,
                               images_placeholder,
                               labels_placeholder)
    true_count += sess.run(eval_correct, feed_dict=feed_dict)
  precision = true_count / num_examples
  print('  Num examples: %d  Num correct: %d  Precision @ 1: %0.04f' %
        (num_examples, true_count, precision))

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

def run_training():
  """Train fully_connected for a number of steps."""
  # Get the sets of images and labels for training, validation, and
  # test on fully_connected.
  # Look at the folder structure, and create lists of all the images.
  data_sets = regression_data.create_image_lists(FLAGS.image_dir, FLAGS.testing_percentage,
                                   FLAGS.validation_percentage)

  # Tell TensorFlow that the model will be built into the default Graph.
  with tf.Graph().as_default():
    # Generate placeholders for the images and labels.
    images_placeholder, labels_placeholder = placeholder_inputs(
        FLAGS.batch_size, name="input_images")

    # Build a Graph that computes predictions from the inference model.
    inference = regression.inference(images_placeholder,
                             FLAGS.hidden1,
                             FLAGS.hidden2)
    # logits = fully_connected.inference(images_placeholder,
    #                                  FLAGS.hidden1,
    #                                  FLAGS.hidden2)
    # softmax = tf.nn.softmax(logits, name="final_result")

    # Add to the Graph the Ops for loss calculation.
    loss = regression.loss(inference, labels_placeholder)

    # Add to the Graph the Ops that calculate and apply gradients.
    train_op = regression.training(loss, FLAGS.learning_rate)

    # Add the Op to compare the logits to the labels during evaluation.
    eval_correct = regression.evaluation(inference, labels_placeholder)

    # Build the summary operation based on the TF collection of Summaries.
    summary_op = tf.merge_all_summaries()

    # Create a saver for writing training checkpoints.
    saver = tf.train.Saver()

    # Create a session for running Ops on the Graph.
    sess = tf.Session()

    # graph = sess.graph

    # Run the Op to initialize the variables.
    init = tf.initialize_all_variables()
    sess.run(init)

    # Instantiate a SummaryWriter to output summaries and the Graph.
    summary_writer = tf.train.SummaryWriter(FLAGS.train_dir,
                                            graph_def=sess.graph_def)

    # And then after everything is built, start the training loop.
    for step in xrange(FLAGS.max_steps):
      start_time = time.time()

      # Fill a feed dictionary with the actual set of images and labels
      # for this particular training step.
      feed_dict = fill_feed_dict(data_sets.train,
                                 images_placeholder,
                                 labels_placeholder)

      # Run one step of the model.  The return values are the activations
      # from the `train_op` (which is discarded) and the `loss` Op.  To
      # inspect the values of your Ops or variables, you may include them
      # in the list passed to sess.run() and the value tensors will be
      # returned in the tuple from the call.
      _, loss_value = sess.run([train_op, loss],
                               feed_dict=feed_dict)

      duration = time.time() - start_time

      # Write the summaries and print an overview fairly often.
      if step % 100 == 0:
        # Print status to stdout.
        print('Step %d: loss = %.2f (%.3f sec)' % (step, loss_value, duration))
        # Update the events file.
        summary_str = sess.run(summary_op, feed_dict=feed_dict)
        summary_writer.add_summary(summary_str, step)

      # Save a checkpoint and evaluate the model periodically.
      if (step + 1) % 1000 == 0 or (step + 1) == FLAGS.max_steps:
        # saver.save(sess, FLAGS.train_dir, global_step=step)
        # Evaluate against the training set.
        print('Training Data Eval:')
        do_eval(sess,
                eval_correct,
                images_placeholder,
                labels_placeholder,
                data_sets.train)
        # Evaluate against the validation set.
        print('Validation Data Eval:')
        do_eval(sess,
                eval_correct,
                images_placeholder,
                labels_placeholder,
                data_sets.validation)
        # Evaluate against the test set.
        print('Test Data Eval:')
        do_eval(sess,
                eval_correct,
                images_placeholder,
                labels_placeholder,
                data_sets.test)

    # result = sess.run(softmax, feed_dict={images_placeholder:input_data.extract_image("/Users/jaruche/Desktop/images/right/image1410.jpg").reshape(1, 120*160)})

    # Write out the trained graph and labels with the weights stored as constants.
    output_graph_def = graph_util.convert_variables_to_constants(
      sess, sess.graph.as_graph_def(), ["final_result"])

    with gfile.FastGFile("output_graph.pb", 'wb') as f:
      f.write(output_graph_def.SerializeToString())


def main(_):
  run_training()


if __name__ == '__main__':
  tf.app.run()