from flask import Flask, request, jsonify, logging  # Import to use web service
import yaml  # Import to read the configuration file information
import settings  # Import setting info
from modules.photo import Photo  # Import Photo module
from modules.video import Video  # Import Video module
from modules.logger import APIAgentLogger
from modules.authentication import authenticate_user  # Import to user authentication
from functools import wraps  # Import to use decorators functions
from lib.flask_celery import make_celery #

##############################################################################################

"""
    API AGENT: Receives requests and interacts with the rest of system elements .
"""

# Main instance app
app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL=settings.API_CELERY_BROKER_URL,
    CELERY_BACKEND=settings.API_CELERY_BACKEND
)

celery = make_celery(app)

# Alert flag, True if there is any to process, False otherwise
motion_agent_alert = False

# Alert photo/video file path
file_path_alert = ""

##############################################################################################

""" Decorator function to access authentication

Returns:
    authentication_sucessfully (bool): True if authentication_sucessfully, False otherwhise      

"""

def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        data = request.get_json()

        if data is not None and 'user' in data and 'password' in data:
            if authenticate_user(data['user'], data['password']):
                return f(*args, **kwargs)
            else:
                return jsonify({'message': 'Autentication is invalid!'}), 401
        else:
            return jsonify({'message': 'Autentication info is missing!'}), 401

    return decorated

##############################################################################################


##############################################################################################


# *********************************************************************************************
# ********************************** API FUNCTIONS ****************************************
# *********************************************************************************************

##############################################################################################

""" Creates an asynchronous task to take a photo

Returns the status and identifier of the task

"""


@app.route("/api/take_photo", methods=['POST'])
@authentication_required
def take_photo_api():
    task = take_photo.delay()

    response = {'status': 'Photo request has been sent', 'task_id': task.id}

    return jsonify(response)


##############################################################################################


""" Creates an asynchronous task to record a video

Returns the status and identifier of the task

"""


@app.route("/api/record_video", methods=['POST'])
@authentication_required
def record_video_api():
    task = record_video.delay(request.get_json())

    if request is not None and 'recordtime' in request and request['recordtime'] > 0:
        record_time = request['recordtime']
    else:
        record_time = 10

    response = {'status': 'A ' + record_time + ' seconds video request has been sent', 'task_id': task.id}

    return jsonify(response)


##############################################################################################

""" Gets task status

Returns the task status ['PENDING','STARTED','FAILURE','REVOKED','SUCCESS']

"""


@app.route("/api/check/<task_id>", methods=['GET'])
def check_api(task_id):
    task = celery.AsyncResult(task_id)
    response = {'status': task.state}

    return jsonify(response)


##############################################################################################


""" Stops task execution

Returns the request status

"""


@app.route("/api/stop/<task_id>", methods=['POST'])
def stop_task_api(task_id):
    task = celery.AsyncResult(task_id)
    print(task.state)

    try:
        celery.control.revoke(task_id, terminate=True)
        response = {'status': 'Task  ' + task_id + " has been stopped successfully"}
    except:
        response = {'status': 'Error while stopping task ' + task_id}

    return jsonify(response)


##############################################################################################


""" Generates a motion alert

Returns the request status

"""

@app.route("/api/generate_motion_agent_alert", methods=['POST'])
@authentication_required
def generate_motion_alert():
    global motion_agent_alert
    global file_path_alert

    try:
        data = request.get_json()
    except:
        return jsonify({'status': 'Error, need credentials and video/photo file path in data request'})

    if data is not None and 'file_path' in data:
        file_path_alert = data['file_path']
        motion_agent_alert = 1
        return jsonify({'status': 'The alert has been received'})
    else:
        return jsonify({'status': 'Error, file path data is missing'}), 400


##############################################################################################

""" Checks if exist a motion alert

Returns True/False. If true, a file_path_alert is added.

"""

@app.route("/api/check_motion_agent_alert", methods=['GET'])
@authentication_required
def check_motion_agent_alert():
    global motion_agent_alert
    print("alert vale {}".format(motion_agent_alert))
    if motion_agent_alert == 1:
        global file_path_alert
        motion_agent_alert = 0
        return jsonify({'alert': True, 'file_path': file_path_alert})
    else:
        return jsonify({'alert': False})

##############################################################################################


##############################################################################################

# *********************************************************************************************
# ********************************** SUPPORT FUNCTIONS ****************************************
# *********************************************************************************************

""" Read photo configuration data from modules config file

Returns:
    data (dict): Photo configuration data

"""


def read_photo_configuration(config_file_path=settings.CONFIG_FILE_MODULE_PATH):
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


def read_video_configuration(config_file_path=settings.CONFIG_FILE_MODULE_PATH):
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

""" Asynchronous task to take a photo

"""


@celery.task(name="api_take_photo")
def take_photo():
    photo_config = read_photo_configuration()

    camera_photo = Photo(file_path=settings.PHOTO_FILES_PATH, resolution=photo_config['resolution'],
                         vflip=photo_config['vflip'], hflip=photo_config['hflip'])
    camera_photo.rotate(photo_config['rotation'])
    camera_photo.take_photo()
    camera_photo.close()


##############################################################################################

""" Asynchronous task to record a video

"""


@celery.task(name="api_record_video")
def record_video(request_data):
    video_config = read_video_configuration()

    video_camera = Video(file_path=settings.VIDEO_FILES_PATH, showDatetime=video_config['showDatetime'],
                         resolution=video_config['resolution'], vflip=video_config['vflip'],
                         hflip=video_config['hflip'])

    video_camera.rotate(video_config['rotation'])

    # If recordtime is specified in the data request
    if request_data is not None and 'recordtime' in request_data and request_data['recordtime'] > 0:
        record_time = request_data['recordtime']

        # Record max long is 1 hour
        if record_time > 3600:
            record_time = 3600
        elif record_time < 0:
            record_time = 5

        video_camera.record_video(record_time)
    # If recordtime is not specified, the default recordtime is 10 seconds.
    else:
        video_camera.record_video()

    video_camera.close()

##############################################################################################

if __name__ == "__main__":
    api_logger = APIAgentLogger()

    # Add a api agent handler to flask logger.
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    log.addHandler(api_logger.get_file_module_handler())
    log.addHandler(api_logger.get_stream_handler())

    app.run(host="0.0.0.0", port=settings.API_AGENT_RUNNING_PORT, debug=settings.DEBUG)

##############################################################################################