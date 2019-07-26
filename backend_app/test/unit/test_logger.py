import unittest
import os
import getpass  # Get username like whoami
import settings

from modules.logger import *

"""
    Logger module unit tests
"""


class TestLoggerModule(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        username = getpass.getuser()
        self.test_path = "/home/" + username
        self.appFileLog = "security_system_PI_APP.log"

        # Logs message
        self.info_message = "TEST: First test message"
        self.warning_message = "TEST: Second test message"
        self.error_message = "TEST: Third test message"
        self.critical_message = "TEST: Fourth test message"

        # Logs level
        self. level_info = "INFO"
        self.level_warning = "WARNING"
        self.level_error = "ERROR"
        self.level_critical = "CRITICAL"


    ##############################################################################################

    def setUp(self):
        self.logger = PhotoLogger(log_path=self.test_path)

    ##############################################################################################

    def test1_create__photo_logger(self):
        logger_name = self.logger.get_logger().name

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertIsNotNone(self.logger)
        self.assertEqual(logger_name, "photo_module")

    ##############################################################################################

    def test2_create_video_logger(self):
        logger = VideoLogger()
        logger_name = logger.get_logger().name

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertIsNotNone(logger)
        self.assertEqual(logger_name, "video_module")

    ##############################################################################################

    def test3_check_log_path(self):
        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(self.logger.log_path, self.test_path)

    ##############################################################################################

    def test3_set_levels(self):
        default_level = self.logger.get_logger().level

        # Test with strings

        self.logger.set_level("INFO")
        info_level_str = self.logger.get_level()

        self.logger.set_level("WARNING")
        warning_level_str = self.logger.get_level()

        self.logger.set_level("ERROR")
        error_level_str = self.logger.get_level()

        self.logger.set_level("CRITICAL")
        critical_level_str = self.logger.get_level()

        self.logger.set_level("DEBUG")
        debug_level_str = self.logger.get_level()

        # Test with numbers

        self.logger.set_level("INFO")
        info_level_num = self.logger.get_level()

        self.logger.set_level("WARNING")
        warning_level_num = self.logger.get_level()

        self.logger.set_level("ERROR")
        error_level_num = self.logger.get_level()

        self.logger.set_level("CRITICAL")
        critical_level_num = self.logger.get_level()

        self.logger.set_level("DEBUG")
        debug_level_num = self.logger.get_level()

        # Test with wrong values

        self.logger.set_level("asdasd")
        wrong_value_1 = self.logger.get_level()

        self.logger.set_level(-1)
        wrong_value_2 = self.logger.get_level()

        self.logger.set_level(500)
        wrong_value_3 = self.logger.get_level()

        self.logger.set_level("ññññññññññ")
        wrong_value_4 = self.logger.get_level()

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        # Checks with numbers
        self.assertEqual(default_level, 10)
        self.assertEqual(info_level_num, 20)
        self.assertEqual(warning_level_num, 30)
        self.assertEqual(error_level_num, 40)
        self.assertEqual(critical_level_num, 50)
        self.assertEqual(debug_level_num, 10)

        # Checks with strings
        self.assertEqual(info_level_str, 20)
        self.assertEqual(warning_level_str, 30)
        self.assertEqual(error_level_str, 40)
        self.assertEqual(critical_level_str, 50)
        self.assertEqual(debug_level_str, 10)

        # Checks with wrong values, value should not change
        self.assertEqual(wrong_value_1, 10)
        self.assertEqual(wrong_value_2, 10)
        self.assertEqual(wrong_value_3, 10)
        self.assertEqual(wrong_value_4, 10)

    ##############################################################################################

    def test4_check_default_handlers(self):
        stream_handler = self.logger.get_stream_handler()
        file_module_handler = self.logger.get_file_module_handler()
        file_app_handler = self.logger.get_file_app_handler()
        file_app_error_handler = self.logger.get_file_app_handler()

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertIsNotNone(stream_handler)
        self.assertIsNotNone(file_module_handler)
        self.assertIsNotNone(file_app_handler)
        self.assertIsNotNone(file_app_error_handler)

    ##############################################################################################

    def test5_check_levels_default_handlers(self):
        stream_handler = self.logger.get_stream_handler()
        file_module_handler = self.logger.get_file_module_handler()
        file_app_handler = self.logger.get_file_app_handler()
        file_app_error_handler = self.logger.get_file_app_error_handler()

        logger_level = self.logger.get_level()
        stream_level = stream_handler.level
        file_module_level = file_module_handler.level
        file_app = file_app_handler.level
        file_app_error = file_app_error_handler.level

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(logger_level, 10)
        self.assertEqual(stream_level, 10)
        self.assertEqual(file_module_level, 20)
        self.assertEqual(file_app, 20)
        self.assertEqual(file_app_error, 40)

    ##############################################################################################

    def test6_check_default_format_handlers(self):
        default_format = '[%(levelname)s:%(asctime)s] %(message)s'
        error_format = '[%(levelname)s:%(asctime)s:%(filename)s:%(funcName)s:%(lineno)dx = set] %(message)s'

        stream_handler_format = self.logger.get_stream_handler().formatter.__dict__.get("_fmt")
        file_module_handler_format = self.logger.get_file_module_handler().formatter.__dict__.get("_fmt")
        file_app_handler_format = self.logger.get_file_app_handler().formatter.__dict__.get("_fmt")
        file_app_error_handler_format = self.logger.get_file_app_error_handler().formatter.__dict__.get("_fmt")

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(stream_handler_format, default_format)
        self.assertEqual(file_module_handler_format, default_format)
        self.assertEqual(file_app_handler_format, default_format)
        self.assertEqual(file_app_error_handler_format, error_format)

    ##############################################################################################

    def test7_video_logging(self):
        video_logger = VideoLogger(log_path=self.test_path)

        # Make logs
        video_logger.info(self.info_message)
        video_logger.warning(self.warning_message)
        video_logger.error(self.error_message)
        video_logger.critical(self.critical_message)

        # Path logs
        video_log_path = self.test_path + "/" + video_logger.logger_name + ".log"
        app_log_path = self.test_path + "/" + app_file_log
        app_error_log_path = self.test_path + "/" + app_file_log_error

        # Check if files exist
        exist_video_log = os.path.isfile(video_log_path)
        exist_app_log = os.path.isfile(app_log_path)
        exist_app_error_log = os.path.isfile(app_error_log_path)

        # Read files
        f_1 = open(video_log_path, "r")
        video_log_content = f_1.read()
        f_1.close()

        f_2 = open(app_log_path, "r")
        app_log_content = f_2.read()
        f_2.close()

        f_3 = open(app_error_log_path, "r")
        app_log_error_content = f_3.read()
        f_3.close()

        # Check if log files have the messages content

        # info level
        video_log_has_message_info = self.info_message in video_log_content and self.level_info in video_log_content
        app_log_has_message_info = self.info_message in app_log_content and self.level_info in app_log_content

        # warning level
        video_log_has_message_warning = self.warning_message in video_log_content and self.level_warning in video_log_content
        app_log_has_message_warning = self.warning_message in app_log_content and self.level_warning in app_log_content

        # level error. In this level it is necessary to check app_log_error file too
        video_log_has_message_error = self.error_message in video_log_content and self.level_error in video_log_content
        app_log_has_message_error = self.error_message in app_log_content and self.level_error in app_log_content
        app_log_error_has_message_error = self.error_message in app_log_error_content and self.level_error in app_log_error_content

        # critical level. In this level it is necessary to check app_log_error file too
        video_log_has_message_critical = self.critical_message in video_log_content and self.level_critical in video_log_content
        app_log_has_message_critical = self.critical_message in app_log_content and self.level_critical in app_log_content
        app_log_error_has_message_critical = self.critical_message in app_log_error_content and self.level_critical in app_log_error_content

        # Remove log files
        os.remove(video_log_path)
        os.remove(app_log_path)
        os.remove(app_error_log_path)

        # Check test files logs after deleting
        exist_video_log_after_deleting = os.path.isfile(video_log_path)
        exist_app_log_after_deleting = os.path.isfile(app_log_path)
        exist_app_error_log_after_deleting = os.path.isfile(app_error_log_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(exist_video_log)
        self.assertTrue(exist_app_log)
        self.assertTrue(exist_app_error_log)

        self.assertTrue(video_log_has_message_info)
        self.assertTrue(app_log_has_message_info)

        self.assertTrue(video_log_has_message_warning)
        self.assertTrue(app_log_has_message_warning)

        self.assertTrue(video_log_has_message_error)
        self.assertTrue(app_log_has_message_error)
        self.assertTrue(app_log_error_has_message_error)

        self.assertTrue(video_log_has_message_critical)
        self.assertTrue(app_log_has_message_critical)
        self.assertTrue(app_log_error_has_message_critical)

        self.assertFalse(exist_video_log_after_deleting)
        self.assertFalse(exist_app_log_after_deleting)
        self.assertFalse(exist_app_error_log_after_deleting)

    ##############################################################################################

    def test8_API_agent_logging(self):
        api_agent_logger = APIAgentLogger(log_path=self.test_path)

        # Make logs
        api_agent_logger.info(self.info_message)
        api_agent_logger.warning(self.warning_message)
        api_agent_logger.error(self.error_message)
        api_agent_logger.critical(self.critical_message)

        # Path logs
        api_agent_log_path = self.test_path + "/" + api_agent_logger.logger_name + ".log"
        app_log_path = self.test_path + "/" + app_file_log
        app_error_log_path = self.test_path + "/" + app_file_log_error

        # Check if files exist
        exist_api_agent_log = os.path.isfile(api_agent_log_path)
        exist_app_log = os.path.isfile(app_log_path)
        exist_app_error_log = os.path.isfile(app_error_log_path)

        # Read files
        f_1 = open(api_agent_log_path, "r")
        api_agent_content = f_1.read()
        f_1.close()

        f_2 = open(app_log_path, "r")
        app_log_content = f_2.read()
        f_2.close()

        f_3 = open(app_error_log_path, "r")
        app_log_error_content = f_3.read()
        f_3.close()

        # Check if log files have the messages content

        # info level
        api_agent_log_has_message_info = self.info_message in api_agent_content and self.level_info in api_agent_content
        app_log_has_message_info = self.info_message in app_log_content and self.level_info in app_log_content

        # warning level
        api_agent_log_has_message_warning = self.warning_message in api_agent_content and self.level_warning in api_agent_content
        app_log_has_message_warning = self.warning_message in app_log_content and self.level_warning in app_log_content

        # level error. In this level it is necessary to check app_log_error file too
        api_agent_log_has_message_error = self.error_message in api_agent_content and self.level_error in api_agent_content
        app_log_has_message_error = self.error_message in app_log_content and self.level_error in app_log_content
        app_log_error_has_message_error = self.error_message in app_log_error_content and self.level_error in app_log_error_content

        # critical level. In this level it is necessary to check app_log_error file too
        api_agent_log_has_message_critical = self.critical_message in api_agent_content and self.level_critical in api_agent_content
        app_log_has_message_critical = self.critical_message in app_log_content and self.level_critical in app_log_content
        app_log_error_has_message_critical = self.critical_message in app_log_error_content and self.level_critical in app_log_error_content

        # Remove log files
        os.remove(api_agent_log_path)
        os.remove(app_log_path)
        os.remove(app_error_log_path)

        # Check test files logs after deleting
        exist_api_agent_log_after_deleting = os.path.isfile(api_agent_log_path)
        exist_app_log_after_deleting = os.path.isfile(app_log_path)
        exist_app_error_log_after_deleting = os.path.isfile(app_error_log_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(exist_api_agent_log)
        self.assertTrue(exist_app_log)
        self.assertTrue(exist_app_error_log)

        self.assertTrue(api_agent_log_has_message_info)
        self.assertTrue(app_log_has_message_info)

        self.assertTrue(api_agent_log_has_message_warning)
        self.assertTrue(app_log_has_message_warning)

        self.assertTrue(api_agent_log_has_message_error)
        self.assertTrue(app_log_has_message_error)
        self.assertTrue(app_log_error_has_message_error)

        self.assertTrue(api_agent_log_has_message_critical)
        self.assertTrue(app_log_has_message_critical)
        self.assertTrue(app_log_error_has_message_critical)

        self.assertFalse(exist_api_agent_log_after_deleting)
        self.assertFalse(exist_app_log_after_deleting)
        self.assertFalse(exist_app_error_log_after_deleting)

    ##############################################################################################

    def test9_motion_agent_logging(self):
        motion_agent_logger = MotionAgentLogger(log_path=self.test_path)

        # Make logs
        motion_agent_logger.info(self.info_message)
        motion_agent_logger.warning(self.warning_message)
        motion_agent_logger.error(self.error_message)
        motion_agent_logger.critical(self.critical_message)

        # Path logs
        motion_agent_log_path = self.test_path + "/" + motion_agent_logger.logger_name + ".log"
        app_log_path = self.test_path + "/" + app_file_log
        app_error_log_path = self.test_path + "/" + app_file_log_error

        # Check if files exist
        exist_motion_agent_log = os.path.isfile(motion_agent_log_path)
        exist_app_log = os.path.isfile(app_log_path)
        exist_app_error_log = os.path.isfile(app_error_log_path)

        # Read files
        f_1 = open(motion_agent_log_path, "r")
        motion_agent_content = f_1.read()
        f_1.close()

        f_2 = open(app_log_path, "r")
        app_log_content = f_2.read()
        f_2.close()

        f_3 = open(app_error_log_path, "r")
        app_log_error_content = f_3.read()
        f_3.close()

        # Check if log files have the messages content

        # info level
        motion_agent_log_has_message_info = self.info_message in motion_agent_content and self.level_info in motion_agent_content
        app_log_has_message_info = self.info_message in app_log_content and self.level_info in app_log_content

        # warning level
        motion_agent_log_has_message_warning = self.warning_message in motion_agent_content and self.level_warning in motion_agent_content
        app_log_has_message_warning = self.warning_message in app_log_content and self.level_warning in app_log_content

        # level error. In this level it is necessary to check app_log_error file too
        motion_agent_log_has_message_error = self.error_message in motion_agent_content and self.level_error in motion_agent_content
        app_log_has_message_error = self.error_message in app_log_content and self.level_error in app_log_content
        app_log_error_has_message_error = self.error_message in app_log_error_content and self.level_error in app_log_error_content

        # critical level. In this level it is necessary to check app_log_error file too
        motion_agent_log_has_message_critical = self.critical_message in motion_agent_content and self.level_critical in motion_agent_content
        app_log_has_message_critical = self.critical_message in app_log_content and self.level_critical in app_log_content
        app_log_error_has_message_critical = self.critical_message in app_log_error_content and self.level_critical in app_log_error_content

        # Remove log files
        os.remove(motion_agent_log_path)
        os.remove(app_log_path)
        os.remove(app_error_log_path)

        # Check test files logs after deleting
        exist_motion_agent_log_after_deleting = os.path.isfile(motion_agent_log_path)
        exist_app_log_after_deleting = os.path.isfile(app_log_path)
        exist_app_error_log_after_deleting = os.path.isfile(app_error_log_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(exist_motion_agent_log)
        self.assertTrue(exist_app_log)
        self.assertTrue(exist_app_error_log)

        self.assertTrue(motion_agent_log_has_message_info)
        self.assertTrue(app_log_has_message_info)

        self.assertTrue(motion_agent_log_has_message_warning)
        self.assertTrue(app_log_has_message_warning)

        self.assertTrue(motion_agent_log_has_message_error)
        self.assertTrue(app_log_has_message_error)
        self.assertTrue(app_log_error_has_message_error)

        self.assertTrue(motion_agent_log_has_message_critical)
        self.assertTrue(app_log_has_message_critical)
        self.assertTrue(app_log_error_has_message_critical)

        self.assertFalse(exist_motion_agent_log_after_deleting)
        self.assertFalse(exist_app_log_after_deleting)
        self.assertFalse(exist_app_error_log_after_deleting)

        ##############################################################################################

    def test10_object_detector_agent_logging(self):
        object_detector_agent_logger = MotionAgentLogger(log_path=self.test_path)

        # Make logs
        object_detector_agent_logger.info(self.info_message)
        object_detector_agent_logger.warning(self.warning_message)
        object_detector_agent_logger.error(self.error_message)
        object_detector_agent_logger.critical(self.critical_message)

        # Path logs
        object_detector_agent_log_path = self.test_path + "/" + object_detector_agent_logger.logger_name + ".log"
        app_log_path = self.test_path + "/" + app_file_log
        app_error_log_path = self.test_path + "/" + app_file_log_error

        # Check if files exist
        exist_object_detector_agent_log = os.path.isfile(object_detector_agent_log_path)
        exist_app_log = os.path.isfile(app_log_path)
        exist_app_error_log = os.path.isfile(app_error_log_path)

        # Read files
        f_1 = open(object_detector_agent_log_path, "r")
        object_detector_agent_content = f_1.read()
        f_1.close()

        f_2 = open(app_log_path, "r")
        app_log_content = f_2.read()
        f_2.close()

        f_3 = open(app_error_log_path, "r")
        app_log_error_content = f_3.read()
        f_3.close()

        # Check if log files have the messages content

        # info level
        object_detector_agent_log_has_message_info = self.info_message in object_detector_agent_content and self.level_info in object_detector_agent_content
        app_log_has_message_info = self.info_message in app_log_content and self.level_info in app_log_content

        # warning level
        object_detector_agent_log_has_message_warning = self.warning_message in object_detector_agent_content and self.level_warning in object_detector_agent_content
        app_log_has_message_warning = self.warning_message in app_log_content and self.level_warning in app_log_content

        # level error. In this level it is necessary to check app_log_error file too
        object_detector_agent_log_has_message_error = self.error_message in object_detector_agent_content and self.level_error in object_detector_agent_content
        app_log_has_message_error = self.error_message in app_log_content and self.level_error in app_log_content
        app_log_error_has_message_error = self.error_message in app_log_error_content and self.level_error in app_log_error_content

        # critical level. In this level it is necessary to check app_log_error file too
        object_detector_agent_log_has_message_critical = self.critical_message in object_detector_agent_content and self.level_critical in object_detector_agent_content
        app_log_has_message_critical = self.critical_message in app_log_content and self.level_critical in app_log_content
        app_log_error_has_message_critical = self.critical_message in app_log_error_content and self.level_critical in app_log_error_content

        # Remove log files
        os.remove(object_detector_agent_log_path)
        os.remove(app_log_path)
        os.remove(app_error_log_path)

        # Check test files logs after deleting
        exist_object_detector_agent_log_after_deleting = os.path.isfile(object_detector_agent_log_path)
        exist_app_log_after_deleting = os.path.isfile(app_log_path)
        exist_app_error_log_after_deleting = os.path.isfile(app_error_log_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(exist_object_detector_agent_log)
        self.assertTrue(exist_app_log)
        self.assertTrue(exist_app_error_log)

        self.assertTrue(object_detector_agent_log_has_message_info)
        self.assertTrue(app_log_has_message_info)

        self.assertTrue(object_detector_agent_log_has_message_warning)
        self.assertTrue(app_log_has_message_warning)

        self.assertTrue(object_detector_agent_log_has_message_error)
        self.assertTrue(app_log_has_message_error)
        self.assertTrue(app_log_error_has_message_error)

        self.assertTrue(object_detector_agent_log_has_message_critical)
        self.assertTrue(app_log_has_message_critical)
        self.assertTrue(app_log_error_has_message_critical)

        self.assertFalse(exist_object_detector_agent_log_after_deleting)
        self.assertFalse(exist_app_log_after_deleting)
        self.assertFalse(exist_app_error_log_after_deleting)

    ##############################################################################################

    def test11_photo_logging(self):

        # Make logs
        self.logger.info(self.info_message)
        self.logger.warning(self.warning_message)
        self.logger.error(self.error_message)
        self.logger.critical(self.critical_message)

        # Path logs
        photo_log_path = self.test_path + "/" + self.logger.logger_name + ".log"
        app_log_path = self.test_path + "/" + app_file_log
        app_error_log_path = self.test_path + "/" + app_file_log_error

        # Check if files exist
        exist_photo_log = os.path.isfile(photo_log_path)
        exist_app_log = os.path.isfile(app_log_path)
        exist_app_error_log = os.path.isfile(app_error_log_path)

        # Read files
        f_1 = open(photo_log_path, "r")
        photo_log_content = f_1.read()
        f_1.close()

        f_2 = open(app_log_path, "r")
        app_log_content = f_2.read()
        f_2.close()

        f_3 = open(app_error_log_path, "r")
        app_log_error_content = f_3.read()
        f_3.close()

        # Check if log files have the messages content

        # info level
        photo_log_has_message_info = self.info_message in photo_log_content and self.level_info in photo_log_content
        app_log_has_message_info = self.info_message in app_log_content and self.level_info in app_log_content

        # warning level
        photo_log_has_message_warning = self.warning_message in photo_log_content and self.level_warning in photo_log_content
        app_log_has_message_warning = self.warning_message in app_log_content and self.level_warning in app_log_content

        # level error. In this level it is necessary to check app_log_error file too
        photo_log_has_message_error = self.error_message in photo_log_content and self.level_error in photo_log_content
        app_log_has_message_error = self.error_message in app_log_content and self.level_error in app_log_content
        app_log_error_has_message_error = self.error_message in app_log_error_content and self.level_error in app_log_error_content

        # critical level. In this level it is necessary to check app_log_error file too
        photo_log_has_message_critical = self.critical_message in photo_log_content and self.level_critical in photo_log_content
        app_log_has_message_critical = self.critical_message in app_log_content and self.level_critical in app_log_content
        app_log_error_has_message_critical = self.critical_message in app_log_error_content and self.level_critical in app_log_error_content

        # Remove log files
        os.remove(photo_log_path)
        os.remove(app_log_path)
        os.remove(app_error_log_path)

        # Check test files logs after deleting
        exist_photo_log_after_deleting = os.path.isfile(photo_log_path)
        exist_app_log_after_deleting = os.path.isfile(app_log_path)
        exist_app_error_log_after_deleting = os.path.isfile(app_error_log_path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(exist_photo_log)
        self.assertTrue(exist_app_log)
        self.assertTrue(exist_app_error_log)

        self.assertTrue(photo_log_has_message_info)
        self.assertTrue(app_log_has_message_info)

        self.assertTrue(photo_log_has_message_warning)
        self.assertTrue(app_log_has_message_warning)

        self.assertTrue(photo_log_has_message_error)
        self.assertTrue(app_log_has_message_error)
        self.assertTrue(app_log_error_has_message_error)

        self.assertTrue(photo_log_has_message_critical)
        self.assertTrue(app_log_has_message_critical)
        self.assertTrue(app_log_error_has_message_critical)

        self.assertFalse(exist_photo_log_after_deleting)
        self.assertFalse(exist_app_log_after_deleting)
        self.assertFalse(exist_app_error_log_after_deleting)


##############################################################################################

if __name__ == '__main__':
    unittest.main()
