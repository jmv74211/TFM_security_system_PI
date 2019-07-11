from picamera import PiCamera
from time import sleep
import time

"""
    Class to administer the photo resource
"""


class Photo:
    """ Constructor

    Parameters:
        file_path (str): Path where save photo files.
        resolution (str): Resolution level. [ULTRA, HIGH, MEDIUM, LOW]. (default is HIGH)
        hflip (bool): Horizontal flip. (default is False)
        vflip (bool): Vertical flip. (default is False)
    """

    def __init__(self, file_path, resolution="HIGH", hflip=False, vflip=False):
        self.file_path = file_path
        self.camera = PiCamera()
        self.resolution = resolution
        self.set_resolution(resolution)
        self.hflip = hflip
        self.vflip = vflip

    ##############################################################################################

    """
  
    Returns a photo name with the current date and time
      
    """

    def get_file_name(self):
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%m")

        hour = time.strftime("%H")
        minute = time.strftime("%M")
        second = time.strftime("%S")

        file_name = "IMG_{}{}{}_{}{}{}.jpg".format(year, month, day, hour, minute, second)

        return file_name

    ##############################################################################################

    """ It allows to set the photo resolution.
        
    Parameters:
        resolution (str): Resolution level. [LOW, MEDIUM, HIGH. ULTRA]. Default HIGHT .
    """

    def set_resolution(self, resolution="HIGH"):

        # Resolution info: https://picamera.readthedocs.io/en/release-1.12/fov.html

        if resolution == "ULTRA":
            # MAX photo resolution: 2592x1944 and MAX Framerate 15
            self.camera.resolution = (2592, 1944)
            self.camera.framerate = 15
            self.resolution = "ULTRA"
        elif resolution == "HIGH":
            self.camera.resolution = (1920, 1080)
            self.camera.framerate = 30
            self.resolution = "HIGH"
        elif resolution == "MEDIUM":
            self.camera.resolution = (1280, 720)
            self.camera.framerate = 40
            self.resolution = "MEDIUM"
        elif resolution == "LOW":
            self.camera.resolution = (640, 480)
            self.camera.framerate = 60
            self.resolution = "LOW"

    ##############################################################################################

    """ It allows to rotate the photo file.

    Parameters:
        degrees (int): number of degrees to rotate
    """

    def rotate(self, degrees):

        degrees = degrees % 360

        if degrees == 0 or degrees == 90 or degrees == 180 or degrees == 270:
            self.camera.rotation = degrees

    ##############################################################################################

    """ It allows activate/deactivate vertical flip.

    Parameters:
        status (bool): Active or deactivated status. Default False.
    """

    def set_vflip(self, status=False):
        self.vflip = status

        if status:
            self.camera.vflip = True

    ##############################################################################################

    """ It allows activate/deactivate horizontal flip.

   Parameters:
       status (bool): Active or deactivated status. Default False.
    """

    def set_hflip(self, status=False):
        self.hflip = status

        if status:
            self.camera.hflip = True

    ##############################################################################################

    """ It allows to capture a photo and save the photo file.
    
    Parameters:
        pauseTime(int): Time (in seconds) to prepare the camera before photo capturing. Default 1 second.
        
    Returns:
        photo_name: Photo name that has been capturated
    
    """

    def take_photo(self, pauseTime=1):
        photo_name = self.file_path + "/" + self.get_file_name()
        self.camera.start_preview()
        sleep(pauseTime)
        self.camera.capture(photo_name)
        self.camera.stop_preview()
        print("Photo has been taken")

        return photo_name

    ##############################################################################################

    """ It allows to capture a photo sequence and save the photo files.

    Parameters:
        num_images(int): Number of photo images to capture. Default 3.
        
    Returns:
        basename: Basename of capturated photos
    """

    def capture_sequence(self, num_images=3):
        basename = self.file_path + "/" + self.get_file_name()
        images_name = []

        for i in range(num_images):
            images_name.append(basename + "-" + repr(i + 1))

        self.camera.start_preview()
        sleep(1)
        self.camera.capture_sequence(images_name)
        self.camera.stop_preview()
        print("Photo sequence has been taken")

        return basename

    ##############################################################################################

    """ It allows to free camera resources.
    
    """

    def close(self):
        self.camera.close()

    ##############################################################################################
