import logging
import sys
from abc import ABC
import settings

##############################################################################################

app_file_log = "security_system_PI_APP.log"
app_file_log_error = "security_system_PI_APP_ERROR.log"

config_log_path = settings.LOGS_FILE_PATH

##############################################################################################


"""
    Abstract parent class to build a logger
"""


class Logger(ABC):
    """ Constructor

        Parameters:
            logger_name (str): Logger name.
            log_path (str): Log path where save log files
    """

    def __init__(self, logger_name, log_path):

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(
            '[%(levelname)s:%(asctime)s] %(message)s'
        )

        self.log_path = log_path
        self.logger_name = logger_name

        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setLevel(logging.DEBUG)
        self.stream_handler.setFormatter(self.formatter)

        self.file_module_handler = logging.FileHandler(self.log_path + "/" + logger_name + ".log")
        self.file_module_handler.setLevel(logging.INFO)
        self.file_module_handler.setFormatter(self.formatter)

        self.file_app_handler = logging.FileHandler(self.log_path + "/" + app_file_log)
        self.file_app_handler.setLevel(logging.INFO)
        self.file_app_handler.setFormatter(self.formatter)

        self.file_app_error_handler = logging.FileHandler(self.log_path + "/" + app_file_log_error)
        self.file_app_error_handler.setLevel(logging.ERROR)
        file_app_error_formatter = logging.Formatter(
            '[%(levelname)s:%(asctime)s:%(filename)s:%(funcName)s:%(lineno)dx = set] %(message)s'
        )
        self.file_app_error_handler.setFormatter(file_app_error_formatter)

        self.logger.addHandler(self.stream_handler)
        self.logger.addHandler(self.file_module_handler)
        self.logger.addHandler(self.file_app_handler)
        self.logger.addHandler(self.file_app_error_handler)

        super().__init__()

    ##############################################################################################

    """ It allows to generate a debug log

    Parameters:
        msg (str): Log message
        
    """

    def debug(self, msg):
        self.logger.debug(msg)

    ##############################################################################################

    """ It allows to generate a info log

    Parameters:
        msg (str): Log message
    
    """

    def info(self, msg):
        self.logger.info(msg)

    ##############################################################################################

    """ It allows to generate a warning log

    Parameters:
         msg (str): Log message

    """

    def warning(self, msg):
        self.logger.warning(msg)

    ##############################################################################################

    """ It allows to generate a error log

    Parameters:
         msg (str): Log message
    
    """

    def error(self, msg):
        self.logger.error(msg)

    ##############################################################################################

    """ It allows to generate a critical log

    Parameters:
        msg (str): Log message
    
    """

    def critical(self, msg):
        self.logger.critical(msg)

    ##############################################################################################

    """

       Returns log path where save log files

    """

    def get_log_path(self):
        return self.log_path

    ##############################################################################################

    """ It allows to set log path

   Parameters:
       new_log_path (str): New log path where save log files

    """

    def set_log_path(self, new_log_path):
        self.log_path = new_log_path

    ##############################################################################################

    """

      Returns logger object

    """

    def get_logger(self):
        return self.logger

    ##############################################################################################

    """ It allows to set the logger object

    Parameters:
       new_logger (logging.logger): New logger 

    """

    def set_logger(self, new_logger):
        if new_logger != None:
            self.logger = new_logger

    ##############################################################################################

    """
                                         [DEBUG,INFO,WARNING,ERROR,CRITICAL]
        Returns logger activation level, [ 10,   20,    30,    40,   50    ]

    """

    def get_level(self):
        return self.logger.level

    ##############################################################################################

    """ It allows to set the logger activation level

    Parameters:
        new_level (str | int): New activation level

   """

    def set_level(self, new_level):
        white_list_str = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        white_list_num = [10, 20, 30, 40, 50]
        if new_level in white_list_str or new_level in white_list_num:
            if new_level == "DEBUG":
                new_level = 10
            elif new_level == "INFO":
                new_level = 20
            elif new_level == "WARNING":
                new_level = 30
            elif new_level == "ERROR":
                new_level = 40
            elif new_level == "CRITICAL":
                new_level = 50

            self.logger.setLevel(new_level)

    ##############################################################################################

    """
                                        
        Returns a formatter log   

    """

    def get_formatter(self):
        return self.formatter

    ##############################################################################################

    """ It allows to set the logger formatter

    Parameters:
        new_formatter (logging.formatter): New formatter to the logger

    """

    def set_formatter(self, new_formatter):
        if new_formatter != None:
            self.formatter = new_formatter

    ##############################################################################################

    """
    
          Returns the stream handler 
    
    """

    def get_stream_handler(self):
        return self.stream_handler

    ##############################################################################################

    """ It allows to set a stream handler 

    Parameters:
        new_stream_handler (logging.streamHandler): New stream handler

   """

    def set_stream_handler(self, new_stream_handler):
        if new_stream_handler != None:
            self.stream_handler = new_stream_handler

    ##############################################################################################

    """

          Returns the module file handler

    """

    def get_file_module_handler(self):
        return self.file_module_handler

    ##############################################################################################

    """ It allows to set a file module handler to store logs related to the module

      Parameters:
          new_file_module_handler (logging.fileHandler): New file handler

     """

    def set_file_module_handler(self, new_file_module_handler):
        if new_file_module_handler != None:
            self.file_module_handler = new_file_module_handler

    ##############################################################################################

    """

        Returns the file app handler

    """

    def get_file_app_handler(self):
        return self.file_app_handler

    ##############################################################################################

    """ It allows to set a app file handler to store all application logs

    Parameters:
        new_file_app_handler (logging.fileHandler): New file handler
    
    """

    def set_file_app_handler(self, new_file_app_handler):
        if new_file_app_handler != None:
            self.file_app_handler = new_file_app_handler

    ##############################################################################################

    """

          Returns the file app error handler

    """

    def get_file_app_error_handler(self):
        return self.file_app_error_handler

    ##############################################################################################

    """ It allows to set a app file error handler to store all error application logs

    Parameters:
        new_file_app_error_handler (logging.fileHandler): New file handler
    
    """

    def set_file_app_error_handler(self, new_file_app_error_handler):
        if new_file_app_error_handler != None:
            self.file_app_error_handler = new_file_app_error_handler

    ##############################################################################################

    """ It allows to add a new handler

    Parameters:
        new_handler (logging.fileHandler): New handler

    """

    def add_handler(self, new_handler):
        if new_handler != None:
            self.logger.addHandler(new_handler)

##############################################################################################


"""
   Photo module logger
"""

class PhotoLogger(Logger):

    def __init__(self, logger_name="photo_module", log_path=config_log_path):
        super().__init__(logger_name, log_path)


##############################################################################################

"""
    Video module logger
"""

class VideoLogger(Logger):

    def __init__(self, logger_name="video_module", log_path=config_log_path):
        super().__init__(logger_name, log_path)

##############################################################################################

"""
    API agent logger
"""

class APIAgentLogger(Logger):

    def __init__(self, logger_name="API_agent", log_path=config_log_path):
        super().__init__(logger_name, log_path)

##############################################################################################

"""
    Motion agent logger
"""

class MotionAgentLogger(Logger):

    def __init__(self, logger_name="motion_agent", log_path=config_log_path):
        super().__init__(logger_name, log_path)

##############################################################################################

"""
    Detector object agent logger
"""

class DetectorObjectAgentLogger(Logger):

    def __init__(self, logger_name="detector_object_agent", log_path=config_log_path):
        super().__init__(logger_name, log_path)

##############################################################################################