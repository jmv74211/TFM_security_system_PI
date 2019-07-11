import unittest
import sys
import time
import os

sys.path.append('../../src')

from modules.photo import Photo

"""
    Photo module unit tests
"""


class TestPhotoModule(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.file_path = "/home/jmv74211"

    ##############################################################################################

    def setUp(self):
        self.camera_photo = Photo(file_path=self.file_path)

    ##############################################################################################

    def tearDown(self):
        self.camera_photo.close()

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
        file_name = "IMG_{}{}{}_{}{}{}.jpg".format(year, month, day, hour, minute, second)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(file_name, self.camera_photo.get_file_name())

    ##############################################################################################

    def test2_get_file_path(self):
        # Get default file path
        current_file_path = self.camera_photo.file_path

        # Change file path
        new_file_path = "/home/user"
        self.camera_photo.file_path = new_file_path
        modified_file_path = self.camera_photo.file_path
        self.camera_photo.close()

        # Add a new Photo object
        path = "/home/random"
        self.camera_photo = Photo(path)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(current_file_path, self.file_path)
        self.assertEqual(new_file_path, modified_file_path)
        self.assertEqual(path, self.camera_photo.file_path)

    ##############################################################################################

    def test3_set_resolution(self):
        # Change resolution values
        current_default_resolution = self.camera_photo.resolution
        current_default_resolution_value = self.camera_photo.camera.resolution
        current_default_framerate = self.camera_photo.camera.framerate

        self.camera_photo.set_resolution("ULTRA")
        current_ultra_resolution = self.camera_photo.resolution
        current_ultra_resolution_value = self.camera_photo.camera.resolution
        current_ultra_framerate = self.camera_photo.camera.framerate

        self.camera_photo.set_resolution("MEDIUM")
        current_medium_resolution = self.camera_photo.resolution
        current_medium_resolution_value = self.camera_photo.camera.resolution
        current_medium_framerate = self.camera_photo.camera.framerate

        self.camera_photo.set_resolution("LOW")
        current_low_resolution = self.camera_photo.resolution
        current_low_resolution_value = self.camera_photo.camera.resolution
        current_low_framerate = self.camera_photo.camera.framerate

        self.camera_photo.set_resolution("adasdadasdas")
        current_error_resolution = self.camera_photo.resolution
        current_error_resolution_value = self.camera_photo.camera.resolution
        current_error_framerate = self.camera_photo.camera.framerate

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertEqual(current_default_resolution, "HIGH")
        self.assertEqual(current_default_resolution_value, (1920, 1080))
        self.assertEqual(current_default_framerate, 30)

        self.assertEqual(current_ultra_resolution, "ULTRA")
        self.assertEqual(current_ultra_resolution_value, (2592, 1944))
        self.assertEqual(current_ultra_framerate, 15)

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
        current_degrees = self.camera_photo.camera.rotation

        # Change degrees
        self.camera_photo.rotate(90)
        state_1 = self.camera_photo.camera.rotation

        # Change to not %90 == 0 value
        self.camera_photo.rotate(120)
        state_2 = self.camera_photo.camera.rotation

        # Change degrees
        self.camera_photo.rotate(180)
        state_3 = self.camera_photo.camera.rotation

        # Test with a value higher than 360
        self.camera_photo.rotate(500)
        state_4 = self.camera_photo.camera.rotation
        self.camera_photo.rotate(900)
        state_5 = self.camera_photo.camera.rotation

        # Change degrees
        self.camera_photo.rotate(270)
        state_6 = self.camera_photo.camera.rotation

        # Test with a negative value
        self.camera_photo.rotate(-30)
        state_7 = self.camera_photo.camera.rotation
        self.camera_photo.rotate(-90)
        state_8 = self.camera_photo.camera.rotation
        self.camera_photo.rotate(-270)
        state_9 = self.camera_photo.camera.rotation

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
        default_value = self.camera_photo.vflip

        self.camera_photo.set_vflip(True)
        activated_value = self.camera_photo.vflip

        self.camera_photo.set_vflip(False)
        deactivated_value = self.camera_photo.vflip

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertFalse(default_value)
        self.assertTrue(activated_value)
        self.assertFalse(deactivated_value)

    ##############################################################################################

    def test6_set_hflip(self):
        default_value = self.camera_photo.hflip

        self.camera_photo.set_hflip(True)
        activated_value = self.camera_photo.hflip

        self.camera_photo.set_hflip(False)
        deactivated_value = self.camera_photo.hflip

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertFalse(default_value)
        self.assertTrue(activated_value)
        self.assertFalse(deactivated_value)

    ##############################################################################################

    def test7_take_photo(self):
        # Take a photo with defalt time 1 sec
        start_time_1 = time.time()
        image_1 = self.camera_photo.take_photo()
        elapsed_time_1 = time.time() - start_time_1

        # Take another photo with 3 seconds delay
        start_time_2 = time.time()
        image_2 = self.camera_photo.take_photo(3)
        elapsed_time_2 = time.time() - start_time_2

        # Check if the images exist in the destination directory
        exist_image_1 = os.path.isfile(image_1)
        exist_image_2 = os.path.isfile(image_2)

        # Delete test images
        os.remove(image_1)
        os.remove(image_2)

        # Check if the images exist in the destination directory
        exist_image_1_after_deleting = os.path.isfile(image_1)
        exist_image_2_after_deleting = os.path.isfile(image_2)

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertGreater(elapsed_time_1, 1)
        self.assertGreater(elapsed_time_2, 3)
        self.assertTrue(exist_image_1)
        self.assertTrue(exist_image_2)
        self.assertFalse(exist_image_1_after_deleting)
        self.assertFalse(exist_image_2_after_deleting)

    ##############################################################################################

    def test8_capture_sequence(self):

        # Capture of 3 photos.
        capture_images_test_1 = 3
        test1_basename = self.camera_photo.capture_sequence(capture_images_test_1)

        # Check if the images exist in the destination directory
        sequence_photo_name_test_1 = []

        for i in range(capture_images_test_1):
            sequence_photo_name_test_1.append(os.path.exists(test1_basename + "-" + repr(i + 1)))

        # Sequence of 5 photos
        capture_images_test_2 = 5
        test2_basename = self.camera_photo.capture_sequence(capture_images_test_2)  # 5 photo captures
        sequence_photo_name_test_2 = []

        for i in range(capture_images_test_2):
            sequence_photo_name_test_2.append(os.path.exists(test2_basename + "-" + repr(i + 1)))

        # Delete test photos
        for i in range(capture_images_test_1):
            os.remove(test1_basename + "-" + repr(i + 1))

        for i in range(capture_images_test_2):
            os.remove(test2_basename + "-" + repr(i + 1))

        sequence_photo_name_test_1_after_deleting = []
        sequence_photo_name_test_2_after_deleting = []

        for i in range(capture_images_test_1):
            sequence_photo_name_test_1_after_deleting.append(os.path.exists(test1_basename + "-" + repr(i + 1)))

        for i in range(capture_images_test_2):
            sequence_photo_name_test_2_after_deleting.append(os.path.exists(test2_basename + "-" + repr(i + 1)))

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        # Photo sequence 1 files created
        for i in range(capture_images_test_1):
            self.assertTrue(sequence_photo_name_test_1[i])

        # Photo sequence 2 files created
        for i in range(capture_images_test_2):
            self.assertTrue(sequence_photo_name_test_2[i])

        # Photo sequence 1 files deleted
        for i in range(capture_images_test_1):
            self.assertFalse(sequence_photo_name_test_1_after_deleting[i])

        # Photo sequence 2 files deleted
        for i in range(capture_images_test_2):
            self.assertFalse(sequence_photo_name_test_2_after_deleting[i])

    ##############################################################################################

    def test9_camera_close(self):
        # Save open status
        camera_state_1 = self.camera_photo.camera.closed

        # Close camera
        self.camera_photo.close()
        camera_state_2 = self.camera_photo.camera.closed

        # ----------------------------------------------------------------------------------------#
        #                                     CHECKS                                              #
        # ----------------------------------------------------------------------------------------#

        self.assertFalse(camera_state_1)
        self.assertTrue(camera_state_2)

##############################################################################################

if __name__ == '__main__':
    unittest.main()
