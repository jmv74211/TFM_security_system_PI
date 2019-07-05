from picamera import PiCamera, Color
from time import sleep
import time
import os

"""
    Class to administer the video resource
"""

class Video:

##############################################################################################

    """
        Constructor class

        Param file_path: Path where save video files.
    """

    def __init__(self,file_path = "/home/jmv74211/Escritorio/"):
        self.file_path = file_path
        self.camera = PiCamera()

##############################################################################################


    """
        Returns a video name with the current date
    """

    def get_file_name(self):
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%m")

        hour = time.strftime("%H")
        minute= time.strftime("%M")
        second = time.strftime("%S")

        file_name = "VID_{}{}{}_{}{}{}.h264".format(year,month,day,hour,minute,second)

        return file_name

##############################################################################################

    """
        It allows to modify the video resolution or add a text inside it.
        Will be improved in next versions.

        Param resolution: Resolution level. Default best.
        Param annotate_text: True for add text to the video. Default false

    """

    def set_configuration(self,resolution="best",annotate_text=False):
        if resolution == "best":
            # Ajustar a resolución máxima: Fotos 2592x1944, Vídeos 1920x1080
            self.camera.resolution = (1920,1080)
            self.camera.framerate = 15
        else:
            self.camera.resolution = (1280,720)
            self.camera.framerate = 15

        if annotate_text:
            self.camera.annotate_text = get_file_name()
            self.camera.annotate_text_size = 50
            self.camera.annotate_background = Color('blue')
            self.camera.annotate_foreground = Color('yellow')

##############################################################################################

    """
        It allows to capture a video and save the file.

        Param time: Record time. Default is 10.
    """
    # Version 1. Problem detected: Only record 60% of total time
    #def record_video(self,time=10):
        #self.camera.start_preview()
        #self.camera.start_recording(self.file_path+ "/" +self.get_file_name())
        #print("Se ha empezado a grabar")
        #self.camera.wait_recording(time)
        #self.camera.stop_recording()
        #self.camera.stop_preview()
        #self.camera.close()
        #print("La grabación ha finalizado")

    def record_video(self,record_time=10):
        sentence = "raspivid -t " + repr(record_time*1000)  +" -o " + self.file_path+ "/" +self.get_file_name()
        process = os.popen(sentence)
        print("Se ha empezado a grabar")
        self.camera.close()
        time.sleep(record_time)
        print("La grabación ha finalizado")

##############################################################################################

    """
        It allows to liberate a camera resource.
    """

    def close(self):
        self.camera.close()

##############################################################################################
