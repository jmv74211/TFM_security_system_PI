import logging
import sys
import yaml
from abc import ABC, abstractmethod

configFile = "../config.yml"
appFileLog = "security_system_PI_APP.log"

class Logger(ABC):

    def __init__(self, loggerName):

        self.logger = logging.getLogger(loggerName)

        self.formatter = logging.Formatter(
            '[%(levelname)s:%(asctime)s:%(module)s] %(message)s'
        )

        with open(configFile, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        self.logPath = cfg['logs']['path']

        self.streamHandler = logging.StreamHandler(sys.stdout)
        self.streamHandler.setLevel(logging.WARNING)
        self.streamHandler.setFormatter(self.formatter)

        self.fileModuleHandler = logging.FileHandler(self.logPath + "/" + loggerName + ".log")
        self.fileModuleHandler.setLevel(logging.DEBUG)
        self.fileModuleHandler.setFormatter(self.formatter)

        self.fileAppHandler = logging.FileHandler(self.logPath + "/" + appFileLog)
        self.fileAppHandler.setLevel(logging.INFO)
        self.fileAppHandler.setFormatter(self.formatter)

        self.logger.addHandler(self.streamHandler)
        self.logger.addHandler(self.fileModuleHandler)
        self.logger.addHandler(self.fileAppHandler)

        super().__init__()

    def getLogPath(self):
        return self.logPath

    def setLogPath(self, newLogPath):
        self.logPath = newLogPath

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self,msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def getLogger(self):
        return self.logger

    def setLogger(self, newLogger):
        if newLogger != None:
            self.logger = newLogger

    def getFormatter(self):
        return self.formatter

    def setFormatter(self, newFormatter):
        if newFormatter != None:
            self.formatter = newFormatter

    def getStreamHandler(self):
        return self.streamHandler

    def setStreamHandler(self, newStreamHandler):
        if newStreamHandler != None:
            self.streamHandler = newStreamHandler


class PhotoLogger(Logger):

    def __init__(self, loggerName = "photoModule"):

        super().__init__(loggerName)


class VideoLogger(Logger):

    def __init__(self, loggerName = "videoModule"):

        super().__init__(loggerName)

