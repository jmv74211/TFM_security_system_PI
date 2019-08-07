import unittest
from agents.object_detector_agent import *
import settings
import os

"""
    Object detector agent unit tests
"""


class TestObjectDetector(unittest.TestCase):

    def test1_get_detector_result(self):

        # Image without people
        image_1_path = os.path.join(settings.ROOT_DIR, 'modules', 'object_detector', 'test_images', '1.jpg')
        # Image with people
        image_2_path = os.path.join(settings.ROOT_DIR, 'modules', 'object_detector', 'test_images', '2.jpg')

        exist_person_image_1 = False
        exist_person_image_2 = False

        object_list_image_1 = get_detector_result(image_1_path)
        object_list_image_2 = get_detector_result(image_2_path)

        for item in object_list_image_1:
            for key, value in item.items():
                if key == 'person':
                    exist_person_image_1 = True

        for item in object_list_image_2:
            for key, value in item.items():
                if key == 'person':
                    exist_person_image_2 = True

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertFalse(exist_person_image_1)
        self.assertTrue(exist_person_image_2)

    ##############################################################################################

