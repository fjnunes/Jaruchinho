import numpy as np
import tensorflow as tf
import os
import os.path
import datetime as dt

import input_data
import model
inf = model.inference()
dir_path = "./images/forward/"
for file in os.listdir(dir_path):
    # image_data = gfile.FastGFile(dir_path+file, 'r').read()
    image_data = input_data.extract_image(dir_path+file)
    image_data = image_data.convert('L')
    image_data = image_data.reshape(1, 19200)
    start = dt.datetime.now()
    result = inf.direction(image_data)
    print(result, (dt.datetime.now()-start).microseconds, file)
