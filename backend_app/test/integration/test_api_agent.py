import unittest
import getpass  # Get username like whoami
from agents.api_agent import *
import json
import os
import time
import requests
import glob


class TestLoggerModule(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # app.testing = True ?
        self.app = app.test_client()
        username = getpass.getuser()
        self.test_path = "/home/" + username

        with open(settings.CONFIG_FILE_AUTHENTICATION, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

        self.user = cfg['authentication']['user']
        self.password = "test"
        self.headers = {'content-type': 'application/json'}
        # self.auth_data = dict(user=self.user, password=self.password)
        self.auth_data = json.dumps({"user": self.user, "password": self.password})
        self.API_url_path = settings.API_AGENT_IP_ADDRESS + ":" + repr(settings.API_AGENT_RUNNING_PORT)

    ##############################################################################################

    def test1_check_authentication(self):

        # Wrong credentials data
        wrong_auth_data_1 = json.dumps({"user": "asd", "password": self.password})
        wrong_auth_data_2 = json.dumps({"user": "asd", "password": "adasd"})
        wrong_auth_data_3 = json.dumps({"user": self.user, "password": "asdad"})

        # Wrong user
        req_1 = self.app.get('/api/motion_agent/check_status', data=wrong_auth_data_1, headers=self.headers)
        # Wrong user and password
        req_2 = self.app.get('/api/motion_agent/check_status', data=wrong_auth_data_2, headers=self.headers)
        # Wrong password
        req_3 = self.app.get('/api/motion_agent/check_status', data=wrong_auth_data_3, headers=self.headers)
        # Auth missing data
        req_4 = self.app.get('/api/motion_agent/check_status', headers=self.headers)
        # Auth data correct
        req_5 = self.app.get('/api/motion_agent/check_status', data=self.auth_data, headers=self.headers)

        # Save message info
        data_response = json.loads(req_1.data.decode('utf8'))
        req1_message = data_response['message']

        data_response = json.loads(req_2.data.decode('utf8'))
        req2_message = data_response['message']

        data_response = json.loads(req_3.data.decode('utf8'))
        req3_message = data_response['message']

        data_response = json.loads(req_4.data.decode('utf8'))
        req4_message = data_response['message']

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        # Check status code
        self.assertEqual(req_1.status_code, 401)
        self.assertEqual(req_2.status_code, 401)
        self.assertEqual(req_3.status_code, 401)
        self.assertEqual(req_4.status_code, 401)
        self.assertEqual(req_5.status_code, 200)

        # Check message data
        self.assertEqual(req1_message, 'Autentication is invalid')
        self.assertEqual(req2_message, 'Autentication is invalid')
        self.assertEqual(req3_message, 'Autentication is invalid')
        self.assertEqual(req4_message, 'Autentication info is missing')

    ##############################################################################################

    def test2_wrong_url(self):
        req = self.app.get('/api/wrongUrl', data=self.auth_data, headers=self.headers)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(req.status_code, 404)

    ##############################################################################################

    """
        NEED CONNECT API AGENT --> Using requests library due to this method needs to interact 
        dynamically  with some API request data, and flask test can not do that.
     """

    def test3_take_photo_api(self):
        url = "/api/take_photo"

        # Take photo request
        req = self.app.post(url, data=self.auth_data, headers=self.headers)
        data_photo_response = json.loads(req.data.decode('utf8'))
        task_id = data_photo_response['task_id']

        # API agent ip addres + port + path
        url_task_result = self.API_url_path + "/api/result/" + task_id
        task_status = ""
        result_photo_path = ""
        task_completed = False

        # While task has not been completed, send a request each 2 seconds to ask again.
        while (not task_completed):  # Do while emulated with break
            try:
                req_2 = requests.get(url_task_result, data=self.auth_data, headers=self.headers)
            except:
                print("API agent is no available. ¿It is connected?")

            data_task_response = req_2.json()
            ready = data_task_response['ready']

            # If task is ready, save result and break while
            if (ready):
                result_photo_path = data_task_response['result']
                task_status = data_task_response['status']
                task_completed = True

            time.sleep(2)

        # Check if image exists
        exist_image = os.path.isfile(result_photo_path)

        # Delete test image
        os.remove(result_photo_path)

        # Check if image exists after deleting
        exist_image_after_deleting = os.path.isfile(result_photo_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(task_status, 'SUCCESS')
        self.assertTrue(exist_image)
        self.assertFalse(exist_image_after_deleting)

    ##############################################################################################

    """
        NEED CONNECT API AGENT --> Using requests library due to this method needs to interact 
        dynamically  with some API request data, and flask test can not do that.
     """

    def test4_record_video_api(self):
        url = "/api/record_video"

        # Record video request
        req = self.app.post(url, data=self.auth_data, headers=self.headers)
        data_video_response = json.loads(req.data.decode('utf8'))
        task_id = data_video_response['task_id']

        # API agent ip addres + port + path
        url_task_result = self.API_url_path + "/api/result/" + task_id
        task_status = ""
        result_video_path = ""
        task_completed = False

        # While task has not been completed, send a request each 2 seconds to ask again.
        while (not task_completed):  # Do while emulated with break
            try:
                req_2 = requests.get(url_task_result, data=self.auth_data, headers=self.headers)
            except:
                print("API agent is no available. ¿It is connected?")

            data_task_response = req_2.json()
            ready = data_task_response['ready']

            # If task is ready, save result and break while
            if (ready):
                result_video_path = data_task_response['result']
                task_status = data_task_response['status']
                task_completed = True

            time.sleep(2)

        # Check if image exists
        exist_video = os.path.isfile(result_video_path)

        # Delete test image
        os.remove(result_video_path)

        # Check if image exists after deleting
        exist_video_after_deleting = os.path.isfile(result_video_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(task_status, 'SUCCESS')
        self.assertTrue(exist_video)
        self.assertFalse(exist_video_after_deleting)

    ##############################################################################################

    """
       NEED CONNECT API AGENT --> Using requests library due to this method needs to interact 
       dynamically  with some API request data, and flask test can not do that.
       
       In this method will take a test photo and will check task status just by sending the request and 
       then, after a few seconds
    """

    def test5_check_task_status(self):
        url = "/api/take_photo"

        # Take photo request
        req = self.app.post(url, data=self.auth_data, headers=self.headers)
        data_photo_response = json.loads(req.data.decode('utf8'))
        task_id = data_photo_response['task_id']

        # API agent ip addres + port + path
        url_task_check = self.API_url_path + "/api/check/" + task_id

        # Request to get task status
        req_2 = requests.get(url_task_check, data=self.auth_data, headers=self.headers)
        req_2_data = req_2.json()
        req_2_status = req_2_data['status']  # STARTED

        # Wait 5 seconds until finishing task
        time.sleep(5)

        # Request to get task status
        req_3 = requests.get(url_task_check, data=self.auth_data, headers=self.headers)
        req_3_data = req_3.json()
        req_3_status = req_3_data['status']  # SUCCESS

        # GET TEST PHOTO RESULT TO DELETE IT
        url_task_result = self.API_url_path + "/api/result/" + task_id
        req_4 = requests.get(url_task_result, data=self.auth_data, headers=self.headers)
        req_4_data = req_4.json()
        req_4_status = req_4_data['status']  # SUCCESS
        test_photo_path = req_4_data['result']

        # Check if image exists
        exist_image = os.path.isfile(test_photo_path)

        # Delete test image
        os.remove(test_photo_path)

        # Check if image exists after deleting
        exist_image_after_deleting = os.path.isfile(test_photo_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(req_2_status, 'STARTED')
        self.assertEqual(req_3_status, 'SUCCESS')
        self.assertEqual(req_4_status, 'SUCCESS')

        self.assertTrue(exist_image)
        self.assertFalse(exist_image_after_deleting)

    ##############################################################################################

    """
       NEED CONNECT API AGENT --> Using requests library due to this method needs to interact 
       dynamically  with some API request data, and flask test can not do that.
    """

    def test6_get_task_result(self):
        url = "/api/take_photo"

        # Take photo request
        req = self.app.post(url, data=self.auth_data, headers=self.headers)
        data_photo_response = json.loads(req.data.decode('utf8'))
        task_id = data_photo_response['task_id']

        # GET TEST PHOTO RESULT
        url_task_result = self.API_url_path + "/api/result/" + task_id
        req_2 = requests.get(url_task_result, data=self.auth_data, headers=self.headers)
        req_2_data = req_2.json()
        req_2_status = req_2_data['status']  # STARTED
        req_2_ready = req_2_data['ready']

        # Wait 5 seconds until finishing task
        time.sleep(5)

        # GET TEST PHOTO RESULT
        url_task_result = self.API_url_path + "/api/result/" + task_id
        req_3 = requests.get(url_task_result, data=self.auth_data, headers=self.headers)
        req_3_data = req_3.json()
        req_3_status = req_3_data['status']  # SUCCESSS
        req_3_ready = req_3_data['ready']
        test_photo_path = req_3_data['result']

        # Check if image exists
        exist_image = os.path.isfile(test_photo_path)

        # Delete test image
        os.remove(test_photo_path)

        # Check if image exists after deleting
        exist_image_after_deleting = os.path.isfile(test_photo_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(req_2_status, 'STARTED')
        self.assertFalse(req_2_ready)
        self.assertEqual(req_3_status, 'SUCCESS')
        self.assertTrue(req_3_ready)

        self.assertTrue(exist_image)
        self.assertFalse(exist_image_after_deleting)

    ##############################################################################################

    """
       NEED CONNECT API AGENT --> Using requests library due to this method needs to interact 
       dynamically  with some API request data, and flask test can not do that.
       
       In this method, I will send a record video request, will check its state and 
       will stop the task, and I will check again its state.
    """

    def test7_stop_result(self):
        url = "/api/record_video"

        # SEND video request
        req = self.app.post(url, data=self.auth_data, headers=self.headers)
        stop_response = json.loads(req.data.decode('utf8'))
        task_id = stop_response['task_id']

        # CHECK TASK STATUS
        url_task_check = self.API_url_path + "/api/check/" + task_id
        req_2 = requests.get(url_task_check, data=self.auth_data, headers=self.headers)
        req_2_data = req_2.json()
        req_2_status = req_2_data['status']  # STARTED

        time.sleep(2)

        # STOP TASK
        url_task_stop = self.API_url_path + "/api/stop/" + task_id
        req_3 = requests.post(url_task_stop, data=self.auth_data, headers=self.headers)
        req_3_data = req_3.json()
        req_3_status = req_3_data['status']  # STARTED
        stop_task_success = 'successfully' in req_3_status  # Message contains successfully that means OK

        # CHECK TASK STATUS
        req_4 = requests.get(url_task_check, data=self.auth_data, headers=self.headers)
        req_4_data = req_4.json()
        req_4_status = req_4_data['status']  # REVOKED

        # DELETE VIDEO FILE
        # get a list of file paths that matches pattern
        fileList = glob.glob(settings.VIDEO_FILES_PATH + "/*.h264")

        # Iterate over the list of filepaths & remove each file.
        for filePath in fileList:
            try:
                os.remove(filePath)
            except OSError:
                print("Error while deleting file")

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(req_2_status, 'STARTED')
        self.assertTrue(stop_task_success)
        self.assertEqual(req_4_status, 'REVOKED')

    ##############################################################################################

    # def test8_activate_deactivate_motion_agent(self):
    #     url_base = settings.API_AGENT_IP_ADDRESS + ":" + repr(settings.API_AGENT_RUNNING_PORT)
    #     url_activate = url_base + "/api/motion_agent/activate"
    #     url_deactivate = url_base + "/api/motion_agent/deactivate"
    #
    #     # Response check messages
    #     activate_photo_mode_message = 'The motion agent in photo mode has been activated sucessfully'
    #     activate_video_mode_message = 'The motion agent in video mode has been activated sucessfully'
    #     already_activated_message = 'The motion agent was already activated'
    #     deactivate_api_message = 'The motion agent has been deactivated sucessfully'
    #     already_deactivated_api_message = 'The motion agent has been deactivated sucessfully'
    #
    #     # Send an activate request
    #     req = requests.post(url_activate, data=self.auth_data, headers=self.headers)
    #     activate_response = req.json()
    #     activate_message = activate_response['status']
    #
    #     time.sleep(1)
    #
    #     # Send again an activate request
    #     req_2 = requests.post(url_activate, data=self.auth_data, headers=self.headers)
    #     activate_response_2 = req_2.json()
    #     activate_message_2 = activate_response_2['status']
    #
    #     time.sleep(1)
    #
    #     # Send a deactivate request
    #     req_3 = requests.post(url_deactivate, data=self.auth_data, headers=self.headers)
    #     deactivate_response = req_3.json()
    #     deactivate_message = deactivate_response['status']
    #
    #     time.sleep(1)
    #
    #     # Send again a deactivate request
    #     req_4 = requests.post(url_deactivate, data=self.auth_data, headers=self.headers)
    #     deactivate_response_2 = req_4.json()
    #     deactivate_message_2 = deactivate_response_2['status']
    #
    #     time.sleep(1)
    #
    #     # Send an activate request in video mode
    #     payload = json.dumps({"user": self.user, "password": self.password, "mode": "video"})
    #     req_5 = requests.post(url_activate, data=payload, headers=self.headers)
    #     activate_response_3 = req_5.json()
    #     activate_message_3 = activate_response_3['status']
    #
    #     time.sleep(1)
    #
    #     # Send a deactivate request in video mode
    #     req_6 = requests.post(url_deactivate, data=self.auth_data, headers=self.headers)
    #     deactivate_response_3 = req_6.json()
    #     deactivate_message_3 = deactivate_response_3['status']
    #
    #     # ----------------------------------------------------------------------------------------#
    #     #                                     CHECKS                                              #
    #     # ----------------------------------------------------------------------------------------#
    #
    #     # Activate default mode (photo)
    #     self.assertEqual(activate_message, activate_photo_mode_message)
    #     self.assertEqual(activate_message_2, already_activated_message)
    #
    #     # Deactivate
    #     self.assertEqual(deactivate_message, deactivate_api_message)
    #     self.assertEqual(deactivate_message_2, already_deactivated_api_message)
    #
    #     # Activate video mode
    #     self.assertEqual(activate_message_3, activate_video_mode_message)
    #
    #     # Deactivate video mode
    #     self.assertEqual(deactivate_message_3, deactivate_api_message)

    ##############################################################################################
