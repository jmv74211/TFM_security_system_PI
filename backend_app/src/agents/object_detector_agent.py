import numpy as np
import os
import tensorflow as tf
from distutils.version import StrictVersion
from PIL import Image
import time
import settings

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
    raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')

from modules.object_detector.utils import label_map_util

##############################################################################################

start_time = time.time()

# What model to download.
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

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

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


##############################################################################################

def get_result(image_path):
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
            object_dict[(category_index.get(value)).get('name')] = scores[0, index]
            objects.append(object_dict)

    return objects


##############################################################################################

# print("--- START GETTING RESULTS %s seconds ---" % (time.time() - start_time))

# print("--- FIRST --> %s seconds ---" % (time.time() - start_time))

objects_1 = get_result(os.path.join(TEST_IMAGES_DIR, 'example.jpg'))
print("Objects_1 = " + objects_1.__repr__())

# print("--- SECOND --> %s seconds ---" % (time.time() - start_time))

objects_2 = get_result(os.path.join(TEST_IMAGES_DIR, '1.jpg'))
print("Objects_2 = " + objects_2.__repr__())

# print("--- THIRD --> %s seconds ---" % (time.time() - start_time))

objects_3 = get_result(os.path.join(TEST_IMAGES_DIR, '2.jpg'))
print("Objects_3 = " + objects_3.__repr__())
# print("--- FOURTH--> %s seconds ---" % (time.time() - start_time))

objects_4 = get_result(os.path.join(TEST_IMAGES_DIR, '3.jpg'))
print("Objects_4 = " + objects_4.__repr__())
# print("--- FINISH AT --> %s seconds ---" % (time.time() - start_time))
