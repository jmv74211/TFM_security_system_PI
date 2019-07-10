import unittest
import sys
import time
import os

sys.path.append('../../src')

from modules.photo import Photo


class TestPhotoModule(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.file_path = "/home/jmv74211"

    def setUp(self):
        self.camera_photo = Photo(file_path=self.file_path)
    
    def tearDown(self):
        self.camera_photo.close()

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

        # Check
        self.assertEqual(file_name, self.camera_photo.get_file_name())

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

        # Checks
        self.assertEqual(current_file_path, self.file_path)

        self.assertEqual(new_file_path, modified_file_path)

        self.assertEqual(path, self.camera_photo.file_path)


    def test3_set_configuration(self):
        current_resolution = self.camera_photo.camera.resolution

        # Change to best resolution (2592,1944) in photo mode.
        self.camera_photo.set_configuration(resolution="best")
        new_resolution = self.camera_photo.camera.resolution

        # Checks
        self.assertEqual(current_resolution, (1920, 1080))
        self.assertEqual(new_resolution, (2592, 1944))


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

        # Checks
        self.assertEqual(current_degrees, 0)
        self.assertEqual(state_1, 90)
        self.assertEqual(state_2, 90)
        self.assertEqual(state_3, 180)
        self.assertEqual(state_4, 90)
        self.assertEqual(state_5, 180)
        self.assertEqual(state_6, 270)

    def test5_take_photo(self):

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

        # Checks
        self.assertGreater(elapsed_time_1, 1)
        self.assertGreater(elapsed_time_2, 3)
        self.assertTrue(exist_image_1)
        self.assertTrue(exist_image_2)

        # Delete test images
        os.remove(image_1)
        os.remove(image_2)

        # Check if the images exist in the destination directory
        exist_image_1 = os.path.isfile(image_1)
        exist_image_2 = os.path.isfile(image_2)

        # Checks
        self.assertFalse(exist_image_1)
        self.assertFalse(exist_image_2)


if __name__ == '__main__':
    unittest.main()
