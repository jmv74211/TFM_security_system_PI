import unittest
import time
import os

from modules.video import Video

"""
    Video module unit tests
"""


class TestVideoModule(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.file_path = "/home/jmv74211"

    ##############################################################################################

    def setUp(self):
        self.camera_video = Video(file_path=self.file_path)

    ##############################################################################################

    def tearDown(self):
        self.camera_video.close()

    ##############################################################################################

    def test1_get_file_name(self):
        # Calculates the current date and time
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%m")

        hour = time.strftime("%H")
        minute = time.strftime("%M")
        second = time.strftime("%S")

        # Template name
        file_name = "VID_{}{}{}_{}{}{}.h264".format(year, month, day, hour, minute, second)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(file_name, self.camera_video.get_file_name())

    ##############################################################################################

    def test2_get_file_path(self):
        # Get default file path
        current_file_path = self.camera_video.file_path

        # Change file path
        new_file_path = "/home/user"
        self.camera_video.file_path = new_file_path
        modified_file_path = self.camera_video.file_path
        self.camera_video.close()

        # Add a new Video object
        path = "/home/random"
        self.camera_video = Video(path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(current_file_path, self.file_path)
        self.assertEqual(new_file_path, modified_file_path)
        self.assertEqual(path, self.camera_video.file_path)

    ##############################################################################################

    def test3_set_resolution(self):
        # Change resolution values
        current_default_resolution = self.camera_video.resolution
        current_default_resolution_value = self.camera_video.camera.resolution
        current_default_framerate = self.camera_video.camera.framerate

        self.camera_video.set_resolution("MEDIUM")
        current_medium_resolution = self.camera_video.resolution
        current_medium_resolution_value = self.camera_video.camera.resolution
        current_medium_framerate = self.camera_video.camera.framerate

        self.camera_video.set_resolution("LOW")
        current_low_resolution = self.camera_video.resolution
        current_low_resolution_value = self.camera_video.camera.resolution
        current_low_framerate = self.camera_video.camera.framerate

        self.camera_video.set_resolution("adasdadasdas")
        current_error_resolution = self.camera_video.resolution
        current_error_resolution_value = self.camera_video.camera.resolution
        current_error_framerate = self.camera_video.camera.framerate

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(current_default_resolution, "HIGH")
        self.assertEqual(current_default_resolution_value, (1920, 1080))
        self.assertEqual(current_default_framerate, 30)

        self.assertEqual(current_medium_resolution, "MEDIUM")
        self.assertEqual(current_medium_resolution_value, (1280, 720))
        self.assertEqual(current_medium_framerate, 40)

        self.assertEqual(current_low_resolution, "LOW")
        self.assertEqual(current_low_resolution_value, (640, 480))
        self.assertEqual(current_low_framerate, 60)

        self.assertEqual(current_error_resolution, "LOW")  # if it is a wrong resolution, value will not
        self.assertEqual(current_error_resolution_value, (640, 480))  # change, so it takes the last one.
        self.assertEqual(current_error_framerate, 60)

    ##############################################################################################

    def test4_set_rotate(self):
        current_degrees = self.camera_video.camera.rotation

        # Change degrees
        self.camera_video.rotate(90)
        state_1 = self.camera_video.camera.rotation

        # Change to not %90 == 0 value
        self.camera_video.rotate(120)
        state_2 = self.camera_video.camera.rotation

        # Change degrees
        self.camera_video.rotate(180)
        state_3 = self.camera_video.camera.rotation

        # Test with a value higher than 360
        self.camera_video.rotate(500)
        state_4 = self.camera_video.camera.rotation
        self.camera_video.rotate(900)
        state_5 = self.camera_video.camera.rotation

        # Change degrees
        self.camera_video.rotate(270)
        state_6 = self.camera_video.camera.rotation

        # Test with a negative value
        self.camera_video.rotate(-30)
        state_7 = self.camera_video.camera.rotation
        self.camera_video.rotate(-90)
        state_8 = self.camera_video.camera.rotation
        self.camera_video.rotate(-270)
        state_9 = self.camera_video.camera.rotation

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(current_degrees, 0)
        self.assertEqual(state_1, 90)
        self.assertEqual(state_2, 90)
        self.assertEqual(state_3, 180)
        self.assertEqual(state_4, 180)
        self.assertEqual(state_5, 180)
        self.assertEqual(state_6, 270)
        self.assertEqual(state_7, 270)
        self.assertEqual(state_8, 270)
        self.assertEqual(state_9, 90)

    ##############################################################################################

    def test5_set_vflip(self):
        default_value = self.camera_video.vflip

        # Change values
        self.camera_video.set_vflip(True)
        activated_value = self.camera_video.vflip

        self.camera_video.set_vflip(False)
        deactivated_value = self.camera_video.vflip

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertFalse(default_value)
        self.assertTrue(activated_value)
        self.assertFalse(deactivated_value)

    ##############################################################################################

    def test6_set_hflip(self):
        default_value = self.camera_video.hflip

        # Change values
        self.camera_video.set_hflip(True)
        activated_value = self.camera_video.hflip

        self.camera_video.set_hflip(False)
        deactivated_value = self.camera_video.hflip

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertFalse(default_value)
        self.assertTrue(activated_value)
        self.assertFalse(deactivated_value)

    ##############################################################################################

    def test7_record_video(self):
        # Record a video with 5 seconds duration
        start_time_1 = time.time()
        video_1 = self.camera_video.record_video(5)
        elapsed_time_1 = time.time() - start_time_1

        # Record another video with 10 seconds duration
        start_time_2 = time.time()
        video_2 = self.camera_video.record_video(10)
        elapsed_time_2 = time.time() - start_time_2

        # Check if the video exist in the destination directory
        exist_video_1 = os.path.isfile(video_1)
        exist_video_2 = os.path.isfile(video_2)

        # Delete test videos
        os.remove(video_1)
        os.remove(video_2)

        # Check if the images exist in the destination directory
        exist_video1_after_deleting = os.path.isfile(video_1)
        exist_video2_after_deleting = os.path.isfile(video_2)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertGreater(elapsed_time_1, 5)
        self.assertGreater(elapsed_time_2, 10)
        self.assertTrue(exist_video_1)
        self.assertTrue(exist_video_2)
        self.assertFalse(exist_video1_after_deleting)
        self.assertFalse(exist_video2_after_deleting)

    ##############################################################################################

    def test8_convert_video_to_mp4(self):
        # Record a video
        video_h264 = self.camera_video.record_video(5, convert_video_to_mp4=False)

        # Convert video to mp4
        exist_video_1 = os.path.isfile(video_h264)
        converted_video = self.camera_video.convert_video_to_mp4(video_h264)
        exist_video_1_after_conversioning = os.path.isfile(video_h264)

        # Delete converted video
        os.remove(converted_video)

        # Check if the images exist in the destination directory
        exist_converted_video = os.path.isfile(converted_video)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(exist_video_1)
        self.assertFalse(exist_video_1_after_conversioning)
        self.assertTrue(video_h264.endswith('.h264'))
        self.assertTrue(converted_video.endswith('.mp4'))
        self.assertFalse(exist_converted_video)

    ##############################################################################################

    def test9_delete_video(self):
        # Record a video
        video_h264 = self.camera_video.record_video(5, convert_video_to_mp4=False)

        # Check if video exist
        exist_video = os.path.isfile(video_h264)

        # Delete video
        self.camera_video.delete_video(video_h264)

        # Check if it exists now
        exist_video_after_deleting = os.path.isfile(video_h264)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertTrue(exist_video)
        self.assertFalse(exist_video_after_deleting)

    ##############################################################################################

    def test10_camera_close(self):
        # Save open status
        camera_state_1 = self.camera_video.camera.closed

        # Close camera
        self.camera_video.close()
        camera_state_2 = self.camera_video.camera.closed

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertFalse(camera_state_1)
        self.assertTrue(camera_state_2)

##############################################################################################

if __name__ == '__main__':
    unittest.main()
