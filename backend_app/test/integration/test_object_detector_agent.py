import unittest
import getpass  # Get username like whoami
from agents.object_detector_agent import *
import json
import os
import time
import requests
import glob
import settings


class TestObjectDetectorAgent(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.app = app.test_client()

        self.username = getpass.getuser()

        self.headers = {'content-type': 'application/json'}

        self.detector_agent_url_path = settings.DETECTOR_AGENT_IP_ADDRESS + ":" + repr(
            settings.DETECTOR_AGENT_RUNNING_PORT)

        self.image_1_path = os.path.join(settings.ROOT_DIR, 'modules', 'object_detector', 'test_images', '1.jpg')

        self.image_2_path = os.path.join(settings.ROOT_DIR, 'modules', 'object_detector', 'test_images', '2.jpg')

    ##############################################################################################

    def test1_wrong_path(self):
        payload = {'file_path': self.image_1_path}

        req = self.app.get('/api/detector_wrong', data=payload, headers=self.headers)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        # Check status code
        self.assertEqual(req.status_code, 404)

    ##############################################################################################

    def test2_get_detector_result_api(self):
        url_object_detector = "/api/detector"
        person_detected_image_1 = False
        person_detected_image_2 = False

        # Missing data
        req = self.app.get(url_object_detector, headers=self.headers)
        req_data = json.loads(req.data.decode('utf8'))
        req_result = req_data['status']

        # Bad data key
        payload = json.dumps({'file': self.image_1_path})
        req_2 = self.app.get(url_object_detector, data=payload, headers=self.headers)
        req_2_data = json.loads(req_2.data.decode('utf8'))
        req_2_result = req_2_data['status']

        # Bad file_path data
        payload_2 = json.dumps({'file_path': '/home/'+ self.username +'/asd.jpg'})
        req_3 = self.app.get(url_object_detector, data=payload_2, headers=self.headers)
        req_3_data = json.loads(req_3.data.decode('utf8'))
        req_3_result = req_3_data['status']

        # Image 1
        payload_3 = json.dumps({'file_path': self.image_1_path})
        req_4 = self.app.get(url_object_detector, data=payload_3, headers=self.headers)
        req_4_data = json.loads(req_4.data.decode('utf8'))
        req_4_result = req_4_data['objects']

        for item in req_4_result:
            for key, value in item.items():
                if key == 'person':
                    person_detected_image_1 = True

        # Image 2
        payload_4 = json.dumps({'file_path': self.image_2_path})
        req_5 = self.app.get(url_object_detector, data=payload_4, headers=self.headers)
        req_5_data = json.loads(req_5.data.decode('utf8'))
        req_5_result = req_5_data['objects']

        for item in req_5_result:
            for key, value in item.items():
                if key == 'person':
                    person_detected_image_2 = True

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        # Check status code
        self.assertEqual(req.status_code, 400)
        self.assertEqual(req_2.status_code, 400)
        self.assertEqual(req_3.status_code, 400)
        self.assertEqual(req_4.status_code, 200)
        self.assertEqual(req_5.status_code, 200)

        # Check message data
        self.assertEqual(req_result, 'Error, bad data request')
        self.assertEqual(req_2_result, 'Error, file_path data missing')
        self.assertEqual(req_3_result, 'Error, file_path does not exist')
        self.assertFalse(person_detected_image_1)
        self.assertTrue(person_detected_image_2)


##############################################################################################
