import os

##################    SERVER CONFIGURATION    ##################

# Root base project dir (src folder)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

##################    STORAGE CONFIGURATION   ##################

# LOGS
LOGS_FILE_PATH = os.path.join(ROOT_DIR,'..', 'logs')

# PATH where save photo and video files.
PHOTO_FILES_PATH = "/home/jmv74211/Escritorio/security_files/photos"
VIDEO_FILES_PATH = "/home/jmv74211/Escritorio/security_files/videos"
ALERTS_FILES_PATH = "/home/jmv74211/Escritorio/security_files/alerts"

##################    CONFIGURATION FILES PATH   ##################

# Module configuration file
CONFIG_FILE_MODULE_PATH = os.path.join(ROOT_DIR, 'config', 'modules_config.yml')

# Credentials file
CONFIG_FILE_AUTHENTICATION = os.path.join(ROOT_DIR, 'config', 'authentication.yml')

##################   API AGENT  ##################

API_AGENT_IP_ADDRESS = "http://192.168.1.100"

# Running port 10000 by default
API_AGENT_RUNNING_PORT = 10000

# DEBUG MODE
DEBUG = True

# Set here your RAW password
API_PASSWORD = os.environ.get('TFM_PASSWORD')

# rabbit-mq server
API_CELERY_BROKER_URL = 'pyamqp://guest@localhost//'

# Database where save tasks states and results
API_CELERY_BACKEND = 'db+sqlite:///api_agent_celery.sqlite'

##################    MOTION AGENT  ##################

# Set the pin GPIO.BOARD where sensor is connected. Default pin 16.
GPIO_SENSOR_PIN_NUMBER = 16

# Time to wait until check movement sensor status
REFRESH_TIME = 5

MOTION_AGENT_PATH = os.path.join(ROOT_DIR, 'agents', 'motion_agent.py')

MOTION_AGENT_CELERY_BACKEND = 'db+sqlite:///motion_agent_celery.sqlite'

##################    STREAMING SERVER  ##################

STREAMING_SERVER_IP_ADDRESS = "http://192.168.1.100"

STREAMING_SERVER_PATH = os.path.join(ROOT_DIR, 'modules', 'pistream', 'streaming_server.py')

STREAMING_SERVER_PORT = 8082

STREAMING_WIDTH = 1024

STREAMING_HEIGHT = 768

STREAMING_FRAME_RATE = 24

##################    DETECTOR_AGENT  ##################

DETECTOR_AGENT_IP_ADDRESS = "http://192.168.1.100"

# Running port 11000 by default
DETECTOR_AGENT_RUNNING_PORT = 11000

# Detector agent status, default False. To activate it, change its value to True
DETECTOR_AGENT_STATUS = True

##################    TELEGRAM BOT  ##################

TELEGRAM_CONFIG_PATH = os.path.join(ROOT_DIR, 'config', 'telegram_config.yml')