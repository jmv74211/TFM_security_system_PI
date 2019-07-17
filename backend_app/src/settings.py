import os

##################    SERVER CONFIGURATION    ##################

# Root base project dir (src folder)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

##################    STORAGE CONFIGURATION   ##################

# LOGS
LOGS_FILE_PATH = "/home/jmv74211/git/TFM_security_system_PI/backend_app/logs"

# PATH where save photo and video files.
PHOTO_FILES_PATH = "/home/jmv74211/Escritorio/security_files/photos"
VIDEO_FILES_PATH =  "/home/jmv74211/Escritorio/security_files/videos"
ALERTS_FILES_PATH = "/home/jmv74211/Escritorio/security_files/alerts"

##################    CONFIGURATION FILES PATH   ##################

# Module configuration file
CONFIG_FILE_MODULE_PATH = os.path.join(ROOT_DIR, 'config','modules_config.yml')

# Credentials file
CONFIG_FILE_AUTHENTICATION =  os.path.join(ROOT_DIR, 'config','authentication.yml')

##################   API AGENT  ##################

# Running port 10000 by default
API_AGENT_RUNNING_PORT = 10000

# DEBUG MODE
DEBUG = True

API_AGENT_IP_ADDRESS = "http://192.168.1.100"

# Set here your RAW password
API_PASSWORD = os.environ.get('TFM_PASSWORD')

# rabbit-mq server
API_CELERY_BROKER_URL = 'pyamqp://guest@localhost//'

# Database where save tasks states and results
API_CELERY_BACKEND = 'db+sqlite:///celery.sqlite'

##################    MOTION AGENT  ##################

# Set the pin where sensor is connected. Default pin 16.
GPIO_SENSOR_PIN_NUMBER = 16

# Time to wait until check movement sensor status
REFRESH_TIME = 5









