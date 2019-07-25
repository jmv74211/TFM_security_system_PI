import numpy as np
import os
import tensorflow as tf
from distutils.version import StrictVersion
from PIL import Image
import settings
from flask import Flask, request, jsonify, logging  # Import to use web service

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
    raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')

from modules.object_detector.utils import label_map_util

##############################################################################################

"""
    OBJECT DETECTOR AGENT: Receives a request a with a photo file path and makes a response with
    a objects detected list detected in that photo.
"""

# Main instance app
app = Flask(__name__)

# Model to use
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

# Project root dir
ROOT_DIR = settings.ROOT_DIR

TEST_IMAGES_DIR = os.path.join(ROOT_DIR, 'modules', 'object_detector', 'test_images')

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = os.path.join(ROOT_DIR, 'modules', 'object_detector', 'models', MODEL_NAME,
                                    'frozen_inference_graph.pb')

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(ROOT_DIR, 'modules', 'object_detector', 'labels', 'mscoco_label_map.pbtxt')

##############################################################################################

## Load the label map.
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.compat.v1.Session(graph=detection_graph)

# Define input and output tensors (i.e. data) for the object detection classifier

image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
# Each box represents a part of the image where a particular object was detected.
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
# Each score represent how level of confidence for each of the objects.
# Score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

##############################################################################################

"""
    Funtion to convert image into numpy array formatted
"""


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


##############################################################################################

"""
    API function that makes a response with a list of objects detected in the photo path
    received.
"""


@app.route("/api/detector", methods=['GET'])
def get_detector_result_api():
    try:
        data = request.get_json()
    except:
        return jsonify({'status': 'Error, bad data request'}), 400

    if data is None or not 'file_path' in data:
        return jsonify({'status': 'Error, file_path data missing'}), 400

    file_path = data['file_path']
    exist_image = os.path.isfile(file_path)

    if not exist_image:
        return jsonify({'status': 'Error, file_path does not exist'}), 400

    objects = get_detector_result(file_path)

    return jsonify({'objects': objects})


##############################################################################################

"""
    Funtion to get the objects detected list in the photo
"""


def get_detector_result(image_path):
    image = Image.open(image_path)
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})
    objects = []
    threshold = 0.5
    for index, value in enumerate(classes[0]):
        object_dict = {}
        if scores[0, index] > threshold:
            object_dict[(category_index.get(value)).get('name')] = float(scores[0, index])
            objects.append(object_dict)

    return objects


##############################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.DETECTOR_AGENT_RUNNING_PORT, debug=False)
