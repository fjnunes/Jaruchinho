import numpy as np
import tensorflow as tf
import os
import os.path
import datetime as dt
import glob
import re

import regression_data
import model

inference = model.inference()

dir_path = "../images/Test/"
file_glob = os.path.join(dir_path, '*.jpg')

for file in glob.glob(file_glob):
    image_data = regression_data.extract_image(file)
    image_data = image_data.reshape([1, 30, 80, 3])
    base_name = os.path.basename(file)
    steering = float(re.search("(\d+)[^_]", base_name).group(0))
    label = (steering - 1552) / (1979 - 980)
    # label = steering
    result = inference.direction(image_data)
    print str(result) +": label: "+str(steering)