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

dir_path = "../images/"
file_glob = os.path.join(dir_path, '*.jpg')

for file in glob.glob(file_glob):
    image_data = regression_data.extract_image(file)
    base_name = os.path.basename(file)
    steering = float(re.search("(\d+)[^_]", base_name).group(0))
    label = (steering - 1552) / (1979 - 980)
    result = inference.direction(image_data)
    print str(result) +": label: "+str(label)