import io
import time
import threading
import picamera
from PIL import Image
import numpy
import model
import serial
import regression_data
import os

# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

startTime = time.time()
inferenceTime = 0
count = 0

if not os.path.exists("images"):
	os.makedirs("images")

serial = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

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
        global serial
        global count
        global startTime
        global inferenceTime

        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    # Read the image and do some processing on it

                    # read values from Arduino
                    with lock:
                        serial.write("B\n")
                        status = serial.read()
                        serial.write("S\n")
                        steering = serial.readline().rstrip()
                        serial.write("T\n")
                        throttle = serial.readline().rstrip()

                    # image is captured regardless of learning / predicting
                    self.stream.seek(0)
                    image = Image.open(self.stream)

                    # Check if transmitter is idle
                    if status != "0":
                        ## Learning - transmitter busy and throttle forward
                        # Read values from Arduino and save as data example along with the image
                        fileName = "images/" + steering+'_'+throttle+'_'+str(count)+".jpg"
                        print fileName
                        image.save(fileName)
                    else:
                        ## Predicting - transmitter idle
                        # Perform forward pass using the image and send command to Arduino
                        # Keep track of time spent on prediction
                        inferenceStart = time.time()
                        image_data = regression_data.extract_image_pil(image)
                        steering, throttle = self.inference.direction(image_data)
                        inferenceTime += time.time()-inferenceStart
                        serial.write("s"+str(steering)+"\n")
                        serial.write("t" + str(throttle) + "\n")

                    # Evaluate frame rate performance
                    count += 1
                    if count % 100 == 0:
                        print "Frame rate: " + str(100 / (time.time() - startTime)) + " Delay: " + str(inferenceTime / 100)
                        startTime = time.time()
                        inferenceTime = 0

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
    pool = [ImageProcessor() for i in range(4)]
    camera.resolution = (320, 240)
    camera.framerate = 20
    time.sleep(2)
    startTime = time.time()
    inferenceTime = 0
    count = 0
    camera.capture_sequence(streams(), use_video_port=True)

# Shut down the processors in an orderly fashion
while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()