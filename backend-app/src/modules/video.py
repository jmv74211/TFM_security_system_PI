from picamera import PiCamera
from picamera import Color
import subprocess
import time
import datetime as dt

"""
    Class to administer the video resource
"""

class Video:
    """ Constructor

    Parameters:
        file_path (str): Path where video photo files.
        showDatetime (bool): Activate/deactivate datetime info in the video
        resolution (str): Resolution level. [HIGH, MEDIUM, LOW]. (default is HIGH)
        hflip (bool): Horizontal flip. (default is False)
        vflip (bool): Vertical flip. (default is False)
    """

    def __init__(self, file_path="/home/jmv74211/Escritorio/", showDatetime=False,
                 resolution="HIGH", hflip=False, vflip=False):
        self.file_path = file_path
        self.camera = PiCamera()
        self.showDatetime = showDatetime
        self.resolution = resolution
        self.set_resolution(resolution)
        self.hflip = hflip
        self.vflip = vflip

    ##############################################################################################

    """
    
    Returns a video name with the current date
    
    """

    def get_file_name(self):
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%m")

        hour = time.strftime("%H")
        minute = time.strftime("%M")
        second = time.strftime("%S")

        file_name = "VID_{}{}{}_{}{}{}.h264".format(year, month, day, hour, minute, second)

        return file_name

    ##############################################################################################

    """ It allows to modify the video resolution.

    Parameters:
        resolution (str): Resolution level. [LOW, MEDIUM, HIGH] (default is HIGHT) .

    """

    def set_resolution(self, resolution="HIGH"):
        # Resolution info: https://picamera.readthedocs.io/en/release-1.12/fov.html

        # MAX video resolution: (1920, 1080) and MAX Framerate 30

        if resolution == "HIGH":
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

    """ It allows to rotate the video file.

    Parameters:
        degrees (int): Number of degrees to rotate
    """

    def rotate(self, degrees):
        self.camera.rotation = degrees % 360

    ##############################################################################################

    """ It allows activate/deactivate vertical flip.

    Parameters:
        status (bool): Active or deactivated status. (default is False).
    """

    def set_vflip(self, status=False):
        self.vflip = status

        if status:
            self.camera.vflip = True

    ##############################################################################################

    """ It allows activate/deactivate horizontal flip.

   Parameters:
       status (bool): Active or deactivated status. (default is False).
    """

    def set_hflip(self, status=False):
        self.hflip = status

        if status:
            self.camera.hflip = True

    ##############################################################################################

    """ It allows to capture a video and save the file. Then, it is converted to mp4 format.

    Parameters:
        record_time (int): Record time. (default is 10).
    """

    def record_video(self, record_time=10):

        video_name = self.file_path + "/" + self.get_file_name()

        if self.showDatetime:
            self.camera.annotate_background = Color('black')
            self.camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.camera.start_recording(video_name)
            print("The recording has started")
            start = dt.datetime.now()
            while (dt.datetime.now() - start).seconds < record_time:
                self.camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.camera.wait_recording(0.2)
            self.camera.stop_recording()
            print("The recording has finished")

        else:
            self.camera.start_preview()
            self.camera.start_recording(video_name)
            print("The recording has started")
            self.camera.wait_recording(record_time)
            self.camera.stop_recording()
            self.camera.stop_preview()
            print("The recording has finished")

        # Convert from .h264 to .mp4
        self.convert_video_to_mp4(video_name)

    ##############################################################################################

    """ It allows to convert from.h264 to mp4 video format.

    Parameters:
        video_path (str): Name of .h264 video path to convert.
    """

    def convert_video_to_mp4(self, video_path):

        video_name_converted = video_path[:-4]  # Deletes h264
        video_name_converted += "mp4"  # Adds new format

        # Make a subprocess. Father process waits until it finishes
        subprocess.call(['MP4Box', '-add', video_path, video_name_converted])

        # Call delete video function
        self.delete_video(video_path)
        print("Video has been converted to mp4")

    ##############################################################################################

    """ It allows to delete de video specified. It is usually called after converting a video.
    
    Parameters:
        video_path (str): Video name path to delete
        
    """

    def delete_video(self, video_path):

        # Make a subprocess for removing. Father process waits until it finishes
        subprocess.call(['rm', video_path])

    ##############################################################################################

    """ It allows to liberate a camera resource.
    
    """

    def close(self):
        self.camera.close()

    ##############################################################################################
