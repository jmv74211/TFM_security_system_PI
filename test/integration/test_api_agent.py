import unittest
import getpass  # Get username like whoami
from agents.api_agent import *
import json
import os
import time
import requests
import glob


class TestAPIAgent(unittest.TestCase):

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

    def test0_check_api_status(self):
        url = os.path.join(self.API_url_path, "api","echo")

        try:
            req = requests.get(url)
        except:
            print("API agent is not running.")
            raise

        self.assertEqual(req.status_code, 200)

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

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_2.status_code, 200)

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

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_2.status_code, 200)

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

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_2.status_code, 200)
        self.assertEqual(req_3.status_code, 200)
        self.assertEqual(req_4.status_code, 200)

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

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_2.status_code, 200)
        self.assertEqual(req_3.status_code, 200)

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

        time.sleep(1)

        # STOP TASK
        url_task_stop = self.API_url_path + "/api/stop/" + task_id
        req_3 = requests.post(url_task_stop, data=self.auth_data, headers=self.headers)
        req_3_data = req_3.json()
        req_3_status = req_3_data['status']  # STARTED
        stop_task_success = 'successfully' in req_3_status  # Message contains successfully that means OK

        time.sleep(2)

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

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_2.status_code, 200)
        self.assertEqual(req_3.status_code, 200)
        self.assertEqual(req_4.status_code, 200)

        self.assertEqual(req_2_status, 'STARTED')
        self.assertTrue(stop_task_success)
        self.assertEqual(req_4_status, 'REVOKED')

    ##############################################################################################

    # activate/deactivate motion agent
    def test8_activate_and_deactivate_ma(self):  # Cant name it with *motion_agent because os.kill will kill it by its name
        url_base = settings.API_AGENT_IP_ADDRESS + ":" + repr(settings.API_AGENT_RUNNING_PORT)
        url_activate = url_base + "/api/motion_agent/activate"
        url_deactivate = url_base + "/api/motion_agent/deactivate"

        # Response check messages
        activate_photo_mode_message = 'The motion agent in photo mode has been activated sucessfully'
        activate_video_mode_message = 'The motion agent in video mode has been activated sucessfully'
        already_activated_message = 'The motion agent was already activated'
        deactivate_api_message = 'The motion agent has been deactivated sucessfully'
        already_deactivated_api_message = 'The motion agent was already deactivated'

        # Send an activate request
        req = requests.post(url_activate, data=self.auth_data, headers=self.headers)
        activate_response = req.json()
        activate_message = activate_response['status']

        time.sleep(0.3)

        # Send again an activate request
        req_2 = requests.post(url_activate, data=self.auth_data, headers=self.headers)
        activate_response_2 = req_2.json()
        activate_message_2 = activate_response_2['status']

        time.sleep(0.3)

        # Send a deactivate request
        req_3 = requests.post(url_deactivate, data=self.auth_data, headers=self.headers)
        deactivate_response = req_3.json()
        deactivate_message = deactivate_response['status']

        time.sleep(0.3)

        # Send again a deactivate request
        req_4 = requests.post(url_deactivate, data=self.auth_data, headers=self.headers)
        deactivate_response_2 = req_4.json()
        deactivate_message_2 = deactivate_response_2['status']

        time.sleep(0.3)

        # Send an activate request in video mode
        payload = json.dumps({"user": self.user, "password": self.password, "mode": "video"})
        req_5 = requests.post(url_activate, data=payload, headers=self.headers)
        activate_response_3 = req_5.json()
        activate_message_3 = activate_response_3['status']

        time.sleep(0.3)

        # Send a deactivate request in video mode
        req_6 = requests.post(url_deactivate, data=self.auth_data, headers=self.headers)
        deactivate_response_3 = req_6.json()
        deactivate_message_3 = deactivate_response_3['status']

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_2.status_code, 200)
        self.assertEqual(req_3.status_code, 200)
        self.assertEqual(req_4.status_code, 200)
        self.assertEqual(req_4.status_code, 200)
        self.assertEqual(req_5.status_code, 200)
        self.assertEqual(req_5.status_code, 200)

        # Activate default mode (photo)
        self.assertEqual(activate_message, activate_photo_mode_message)
        self.assertEqual(activate_message_2, already_activated_message)

        # Deactivate
        self.assertEqual(deactivate_message, deactivate_api_message)
        self.assertEqual(deactivate_message_2, already_deactivated_api_message)

        # Deactivate video mode
        self.assertEqual(deactivate_message_3, deactivate_api_message)

        # Activate video mode
        self.assertEqual(activate_message_3, activate_video_mode_message)

    ##############################################################################################

    # check_motion_agent_status()
    def test9_check_status_ma(self):  # Cant name it with *motion_agent because os.kill will kill it by its name
        url_base = settings.API_AGENT_IP_ADDRESS + ":" + repr(settings.API_AGENT_RUNNING_PORT)
        url_activate = url_base + "/api/motion_agent/activate"
        url_deactivate = url_base + "/api/motion_agent/deactivate"
        url_check = url_base + "/api/motion_agent/check_status"

        # Send check request
        req = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_response = req.json()
        check_message = check_response['status']

        time.sleep(0.3)

        # Send an activate request
        req_2 = requests.post(url_activate, data=self.auth_data, headers=self.headers)
        time.sleep(0.3)

        # Send check request
        req_3 = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_response_2 = req_3.json()
        check_message_2 = check_response_2['status']

        time.sleep(0.3)

        # Send a deactivate request
        req_4 = requests.post(url_deactivate, data=self.auth_data, headers=self.headers)

        time.sleep(0.3)

        # Send check request
        req_5 = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_response_3 = req_5.json()
        check_message_3 = check_response_3['status']

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_2.status_code, 200)
        self.assertEqual(req_3.status_code, 200)
        self.assertEqual(req_4.status_code, 200)
        self.assertEqual(req_5.status_code, 200)

        self.assertEqual(check_message, 'OFF')
        self.assertEqual(check_message_2, 'ON')
        self.assertEqual(check_message_3, 'OFF')

    ##############################################################################################

    def test10_generate_and_check_motion_alert(self):
        url_base = settings.API_AGENT_IP_ADDRESS + ":" + repr(settings.API_AGENT_RUNNING_PORT)
        url_generate = url_base + "/api/motion_agent/generate_alert"
        url_check = url_base + "/api/motion_agent/check_alert"

        # Send generate request with missing file data
        req_2 = requests.post(url_generate, data=self.auth_data, headers=self.headers)
        generate_response = req_2.json()
        generate_message = generate_response['status']

        time.sleep(0.3)

        # Send check request
        req_3 = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_alert_response_2 = req_3.json()
        check_alert_message_2 = check_alert_response_2['alert']

        time.sleep(0.3)

        # Send generate request with file data
        payload = json.dumps({'user': self.user, 'password': self.password, 'file_path': './IMG_212.jpg'})
        req_4 = requests.post(url_generate, data=payload, headers=self.headers)
        generate_response_2 = req_4.json()
        generate_message_2 = generate_response_2['status']

        time.sleep(0.3)

        # Send check request
        req_5 = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_alert_response_3 = req_5.json()
        check_alert_message_3 = check_alert_response_3['alert']
        file_path_message = check_alert_response_3['file_path']

        time.sleep(0.3)

        # Send check request again to verify that notification is set to 0
        req_6 = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_alert_response_4 = req_6.json()
        check_alert_message_4 = check_alert_response_4['alert']

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(req_2.status_code, 400)
        self.assertEqual(req_3.status_code, 200)
        self.assertEqual(req_4.status_code, 200)
        self.assertEqual(req_5.status_code, 200)
        self.assertEqual(req_6.status_code, 200)

        self.assertEqual(generate_message, 'Error, file path data is missing')
        self.assertFalse(check_alert_message_2)
        self.assertEqual(generate_message_2, 'The alert has been received')
        self.assertTrue(check_alert_message_3)
        self.assertEqual(file_path_message, './IMG_212.jpg')
        self.assertFalse(check_alert_message_4)

    ##############################################################################################

    def test11_activate_check_deactivate_sv(self): # Streaming server
        url_base = settings.API_AGENT_IP_ADDRESS + ":" + repr(settings.API_AGENT_RUNNING_PORT)
        url_activate = url_base + "/api/streaming/activate"
        url_deactivate = url_base + "/api/streaming/deactivate"
        url_check = url_base + "/api/streaming/check_status"

        # Send check request
        req = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_status_response = req.json()
        check_status_message = check_status_response['status']

        # Send an activate response
        req_2 = requests.post(url_activate, data=self.auth_data, headers=self.headers)
        activate_response = req_2.json()
        activate_message = activate_response['status']

        # Send check request
        req_3 = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_status_response_2 = req_3.json()
        check_status_message_2 = check_status_response_2['status']

        # Send a deactivate request
        req_4 = requests.post(url_deactivate, data=self.auth_data, headers=self.headers)
        deactivate_response = req_4.json()
        deactivate_message = deactivate_response['status']

        # Send check request
        req_5 = requests.get(url_check, data=self.auth_data, headers=self.headers)
        check_status_response_3 = req_5.json()
        check_status_message_3 = check_status_response_3['status']

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_2.status_code, 200)
        self.assertEqual(req_3.status_code, 200)
        self.assertEqual(req_4.status_code, 200)
        self.assertEqual(req_5.status_code, 200)

        self.assertEqual(check_status_message, 'OFF')
        self.assertEqual(activate_message, 'The streaming mode has been activated sucessfully')
        self.assertEqual(check_status_message_2, 'ON')
        self.assertEqual(deactivate_message, 'The streaming server has been stopped sucessfully')
        self.assertEqual(check_status_message_3, 'OFF')

    ##############################################################################################


##############################################################################################

