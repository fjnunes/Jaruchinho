import io
import time
import threading
import picamera
from PIL import Image
import numpy
import model

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

startTime = time.time()
count = 0

class ImageProcessor(threading.Thread):

    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.inference = model.inference()
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    image = Image.open(self.stream)
                    image = image.convert('L')  # makes it greyscale
                    image = image.crop((0, 60, 160, 120))
                    image_data = numpy.array(image)
                    image_data = image_data.reshape(1, 19200 / 2)
                    command = self.inference.direction(image_data)

                    global count
                    global startTime
                    count += 1
                    if count % 100 == 0:
                        print count / (time.time() - startTime)
                        startTime = time.time()
                        count = 0

                    #...
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #done=True
                except KeyboardInterrupt:
                    done = True
                    pass
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)

def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            time.sleep(0.01)

with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(12)]
    camera.resolution = (320, 240)
    camera.framerate = 90
    time.sleep(2)
    startTime = time.time()
    count = 0
    camera.capture_sequence(streams(), use_video_port=True)

# Shut down the processors in an orderly fashion
while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()