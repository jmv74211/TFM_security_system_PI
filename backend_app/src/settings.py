import os


##################    SERVER CONFIGURATION    ##################

# Root base project dir (src folder)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 10000 by default
API_AGENT_RUNNING_PORT = 10000

# DEBUG MODE
DEBUG = True

##################    STORAGE CONFIGURATION   ##################

# LOGS
LOGS_FILE_PATH = "/home/jmv74211/git/TFM_security_system_PI/backend_app/logs"

# PATH where save photo and video files.
PHOTO_FILES_PATH = "/home/jmv74211/Escritorio/security_files/photos"
VIDEO_FILES_PATH =  "/home/jmv74211/Escritorio/security_files/videos"

##################    CONFIGURATION FILES PATH   ##################

# Module configuration file
CONFIG_FILE_MODULE_PATH = os.path.join(ROOT_DIR, 'config','modules_config.yml')

# Credentials file
CONFIG_FILE_AUTHENTICATION =  os.path.join(ROOT_DIR, 'config','authentication.yml')










