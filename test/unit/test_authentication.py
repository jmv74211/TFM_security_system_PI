from modules.authentication import authenticate_user
import unittest
import settings
import yaml
import getpass  # Get username like whoami


class TestAPIAgentModule(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        username = getpass.getuser()
        self.test_path = "/home/" + username

    ##############################################################################################

    def test1_authenticate_user(self):

        with open(settings.CONFIG_FILE_AUTHENTICATION, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

        check_1 = authenticate_user(cfg['authentication']['user'], settings.API_PASSWORD) # Correct
        check_2 = authenticate_user("aasdas34f", "test")
        check_3 = authenticate_user("userTest", "hest" )
        check_4 = authenticate_user("usa12", "hdas2")


        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(check_1)
        self.assertFalse(check_2)
        self.assertFalse(check_3)
        self.assertFalse(check_4)

    ##############################################################################################