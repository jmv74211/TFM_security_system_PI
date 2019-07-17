import unittest
import getpass  # Get username like whoami
import settings
from agents.api_agent import *
import json
import os


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

    # def test1_authentication(self):
    #     url = "/api/take_photo"
    #     wrong_url = "/api/wrong_path"
    #
    #     req = self.app.post(url, data=self.auth_data, headers=self.headers)

    def test2_take_photo(self):

        files_path = os.path.join(self.test_path,"test_security_files")
        os.mkdir(files_path)

        url = "/api/take_photo"
        wrong_url = "/api/wrong_path"

        req = self.app.post(url, data=self.auth_data, headers=self.headers)
        wrong_req = self.app.post(wrong_url, data=self.auth_data, headers=self.headers)

        data_response = json.loads(req.data.decode('utf8'))
        status_message = data_response['status']

        self.assertEqual(req.status_code, 200)
        self.assertEqual(wrong_req.status_code, 404)
        self.assertEqual(status_message, "Photo has been taken")

    def test2_record_video(self):
        url = "/api/record_video"
        wrong_url = "/api/wrong_path"

        request_data_1 = json.dumps({"user": self.user, "password": self.password, "recordtime": 3})
        request_data_2 = json.dumps({"user": self.user, "password": self.password, "recordtime": -2})

        req = self.app.post(url, data=self.auth_data, headers=self.headers)
        req_1 = self.app.post(url, data=request_data_1, headers=self.headers)
        req_2 = self.app.post(url, data=request_data_2, headers=self.headers)
        wrong_req = self.app.post(wrong_url, data=self.auth_data, headers=self.headers)

        data_response = json.loads(req.data.decode('utf8'))
        status_message = data_response['status']

        data_response_1 = json.loads(req.data.decode('utf8'))
        status_message_1 = data_response_1['status']

        data_response_2 = json.loads(req.data.decode('utf8'))
        status_message_2 = data_response_2['status']

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_1.status_code, 200)
        self.assertEqual(req_2.status_code, 200)
        self.assertEqual(wrong_req.status_code, 404)

        self.assertEqual(status_message, "A 10 seconds video has been recorded!")
        self.assertEqual(status_message_1, "A 3 seconds video has been recorded!")
        self.assertEqual(status_message_2, "A 5 seconds video has been recorded!")