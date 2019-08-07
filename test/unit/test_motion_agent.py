import unittest

from agents.motion_agent import *

"""
    Motion agent unit tests
"""


class TestMotionAgent(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    ##############################################################################################

    def setUp(self):
        celery.conf.update(task_always_eager=True)

    ##############################################################################################

    def test1_detect_person(self):
        object_list_1 = {"objects": [{'bike': 0.65}, {'cup': 0.5}]}
        object_list_2 = {"objects": [{'bike': 0.65}, {'cup': 0.5}, {'person': 0.85}]}
        object_list_3 = {"objects": []}

        detected_person_object_list_1 = detect_person(object_list_1)
        detected_person_object_list_2 = detect_person(object_list_2)
        detected_person_object_list_3 = detect_person(object_list_3)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertFalse(detected_person_object_list_1)
        self.assertTrue(detected_person_object_list_2)
        self.assertFalse(detected_person_object_list_3)

    ##############################################################################################

    def test2_send_object_detector_agent_request(self):

        test_image_with_person = os.path.join(settings.ROOT_DIR, 'modules', 'object_detector', 'test_images', '2.jpg')
        test_image_without_person = os.path.join(settings.ROOT_DIR, 'modules', 'object_detector', 'test_images', '1.jpg')

        check_test_image_with_person = send_object_detector_agent_request(test_image_with_person)
        check_test_image_without_person = send_object_detector_agent_request(test_image_without_person)


        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(check_test_image_with_person)
        self.assertFalse(check_test_image_without_person)

    ##############################################################################################

    def test3_generate_api_agent_alert(self):

        request_sent = generate_api_agent_alert('photo_file_path')

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(request_sent)

##############################################################################################

if __name__ == '__main__':
    unittest.main()
