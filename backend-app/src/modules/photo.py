from picamera import PiCamera, Color
from time import sleep
import time

"""
    Class to administer the photo resource
"""

class Photo:

##############################################################################################

    """
        Constructor class

        Param file_path: Path where save photo files.
    """

    def __init__(self,file_path):
        self.file_path = file_path
        self.camera = PiCamera()

##############################################################################################

    """
        Returns a photo name with the current date
    """

    def get_file_name(self):
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%m")

        hour = time.strftime("%H")
        minute= time.strftime("%M")
        second = time.strftime("%S")

        file_name = "IMG_{}{}{}_{}{}{}.jpg".format(year,month,day,hour,minute,second)

        return file_name

##############################################################################################


    """
        It allows to modify the photo resolution or add a text inside it.
        Will be improved in next versions.

        Param resolution: Resolution level. Default best.
        Param annotate_text: True for add text to the photo. Default false
    """
    def set_configuration(self,resolution="best",annotate_text=False):
        if resolution == "best":
            # Ajustar a resolución máxima: Fotos 2592x1944, Vídeos 1920x1080
            self.camera.resolution = (2592,1944)
            self.camera.framerate = 15
        else:
            self.camera.resolution = (1728,1296)
            self.camera.framerate = 15

        if annotate_text:
            self.camera.annotate_text = get_file_name()
            self.camera.annotate_text_size = 50
            self.camera.annotate_background = Color('blue')
            self.camera.annotate_foreground = Color('yellow')

##############################################################################################

    """
        It allows to rotate the photo file.

        Param grades: Number of rotation grades.
    """
    def rotate(self,grades):
            self.camera.rotation = grades % 360

##############################################################################################

    """
        It allows to capture a photo and save the file.

        Param pauseTime: Time (in seconds) to prepare the camera before photo capturing.
                         Default 1 second.
    """
    def take_photo(self,pauseTime=1):
        self.camera.start_preview()
        sleep(pauseTime)
        self.camera.capture(self.file_path+ "/" +self.get_file_name())
        self.camera.stop_preview()
        self.camera.close()
        print("Photo has been taken")

##############################################################################################

    """
        It allows to liberate a camera resource.
    """
    def close(self):
        self.camera.close()

##############################################################################################
