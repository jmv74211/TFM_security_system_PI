from flask import Flask, request, jsonify, logging  # Import to use web service
import yaml  # Import to read the configuration file information
import settings  # Import setting info
from modules.photo import Photo  # Import Photo module
from modules.video import Video  # Import Video module
from modules.logger import APIAgentLogger
from modules.authentication import authenticate_user  # Import to user authentication
from functools import wraps                    # Import to use decorators functions

##############################################################################################

"""
    MAIN AGENT: Receives requests and interacts with the rest of system elements .
"""

# Main instance app
app = Flask(__name__)

# *********************************************************************************************
# ********************************** SUPPORT FUNCTIONS ****************************************
# *********************************************************************************************

""" Decorator function to access authentication

Returns:
    authentication_sucessfully (bool): True if authentication_sucessfully, False otherwhise      

"""


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        data = request.get_json()

        if data is not None and 'username' in data and 'password' in data:
            if authenticate_user(data['username'], data['password']):
                return f(*args, **kwargs)
            else:
                return jsonify({'message': 'Autentication is invalid!'}), 401
        else:
            return jsonify({'message': 'Autentication info is missing!'}), 401

    return decorated


##############################################################################################

""" Read photo configuration data from modules config file

Returns:
    data (dict): Photo configuration data

"""


def read_photo_configuration(config_file_path = settings.CONFIG_FILE_MODULE_PATH):
    with open(config_file_path, 'r') as ymlfile:
        module_settings = yaml.load(ymlfile, Loader=yaml.FullLoader)

    data = dict()

    data['resolution'] = module_settings['photo']['resolution']
    data['rotation'] = module_settings['photo']['rotation']
    data['vflip'] = module_settings['photo']['vflip']
    data['hflip'] = module_settings['photo']['hflip']

    return data


##############################################################################################

""" Read video configuration data from modules config file

Returns:
    data (dict): Video configuration data

"""


def read_video_configuration(config_file_path = settings.CONFIG_FILE_MODULE_PATH):
    with open(config_file_path, 'r') as ymlfile:
        module_settings = yaml.load(ymlfile, Loader=yaml.FullLoader)

    data = dict()

    data['resolution'] = module_settings['video']['resolution']
    data['rotation'] = module_settings['video']['rotation']
    data['vflip'] = module_settings['video']['vflip']
    data['hflip'] = module_settings['video']['hflip']
    data['showDatetime'] = module_settings['video']['showDatetime']

    return data


##############################################################################################


#*********************************************************************************************
#********************************** API FUNCTIONS ****************************************
#*********************************************************************************************

##############################################################################################

@app.route("/api/take_photo", methods=['POST'])
@authentication_required
def take_photo():
    photo_config = read_photo_configuration()

    camera_photo = Photo(file_path=settings.PHOTO_FILES_PATH, resolution=photo_config['resolution'],
                         vflip=photo_config['vflip'], hflip=photo_config['hflip'])
    camera_photo.rotate(photo_config['rotation'])
    camera_photo.take_photo()
    camera_photo.close()

    response = {'status': 'Photo has been taken'}

    return jsonify(response)


##############################################################################################

@app.route("/api/record_video", methods=['POST'])
@authentication_required
def record_video():
    video_config = read_video_configuration()

    video_camera = Video(file_path=settings.VIDEO_FILES_PATH, showDatetime=video_config['showDatetime'],
                         resolution=video_config['resolution'], vflip=video_config['vflip'],
                         hflip=video_config['hflip'])

    video_camera.rotate(video_config['rotation'])

    data = request.get_json()

    # If recordtime is specified in the data request
    if data is not None and 'recordtime' in data and data['recordtime'] > 0:
        record_time = data['recordtime']
        # Record max long is 1 hour
        if (record_time > 3600):
            record_time = 3600
        video_camera.record_video(record_time)
    # If recordtime is not specified, the default recordtime is 10 seconds.
    else:
        video_camera.record_video()

    video_camera.close()

    response = {'status': 'Video recorded!'}

    return jsonify(response)


##############################################################################################

if __name__ == "__main__":
    api_logger = APIAgentLogger()

    # Add a api agent handler to flask logger.
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    log.addHandler(api_logger.get_file_module_handler())
    log.addHandler(api_logger.get_stream_handler())

    app.run(host="0.0.0.0", port=settings.API_AGENT_RUNNING_PORT, debug=settings.DEBUG)
