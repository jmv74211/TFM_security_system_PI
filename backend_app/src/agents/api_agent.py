from flask import Flask, request, jsonify, logging  # Import to use web service
import yaml  # Import to read the configuration file information
import settings  # Import setting info
from modules.photo import Photo  # Import Photo module
from modules.video import Video  # Import Video module
from modules.logger import APIAgentLogger
from modules.authentication import authenticate_user  # Import to user authentication
from functools import wraps  # Import to use decorators functions
from lib.flask_celery import make_celery  #
import os
import time
import signal
import subprocess  # Import to create a synchronous processes
import json

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

        try:
            data = json.loads(request.data.decode('utf-8'),
                              strict=False)  # strict = False allow for escaped chardata = request.get_json()
            if data is not None and 'user' in data and 'password' in data:
                if authenticate_user(data['user'], data['password']):
                    return f(*args, **kwargs)
                # User or password invalid
                else:
                    return jsonify({'message': 'Autentication is invalid'}), 401
            # User or password info missing
            else:
                return jsonify({'message': 'Autentication info is missing'}), 401
        # Missing data
        except:
            return jsonify({'message': 'Autentication info is missing'}), 401

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
    try:
        task = take_photo.delay()
        return jsonify({'status': 'Photo request has been sent', 'task_id': task.id})
    except:
        log.error("Error when creating the asynchronous task to take a photo", exc_info=True)
        return jsonify({'status': 'Error, please try again'}), 500


##############################################################################################


""" Creates an asynchronous task to record a video

Returns the status and identifier of the task

"""


@app.route("/api/record_video", methods=['POST'])
@authentication_required
def record_video_api():
    try:
        data = request.get_json()
    except:
        return jsonify({'status': 'Error, bad data request'}), 400

    if data is not None and 'recordtime' in data and data['recordtime'] > 0:
        record_time = data['recordtime']
    else:
        record_time = 10

    try:
        task = record_video.delay(record_time)
        response = {'status': 'A ' + repr(record_time) + ' seconds video request has been sent', 'task_id': task.id}
        return jsonify(response)
    except:
        log.error("Error when creating the asynchronous task to record a photo", exc_info=True)
        return jsonify({'status': 'Error, please try again'}), 500


##############################################################################################

""" Gets task status

Returns the task status ['PENDING','STARTED','FAILURE',RETRY,'REVOKED','SUCCESS']

"""


@app.route("/api/check/<task_id>", methods=['GET'])
@authentication_required
def check_task_status_api(task_id):
    task = celery.AsyncResult(task_id)
    response = {'status': task.state}
    return jsonify(response)


##############################################################################################

""" Gets task result

Returns: 
"""


@app.route("/api/result/<task_id>", methods=['GET'])
@authentication_required
def get_task_result_api(task_id):
    task = celery.AsyncResult(task_id)

    if task.ready():
        response = {'ready': True, 'status': task.state, 'result': task.get()}
    else:
        response = {'ready': False, 'status': task.state}

    return jsonify(response)


##############################################################################################


""" Stops task execution

Returns the request status

"""


@app.route("/api/stop/<task_id>", methods=['POST'])
@authentication_required
def stop_task_api(task_id):
    try:
        celery.control.revoke(task_id, terminate=True)
        response = {'status': 'Task  ' + task_id + " has been stopped successfully"}
        return jsonify(response)
    except:
        response = {'status': 'Error while stopping task ' + task_id}
        log.error("Error when stopping a task with id = {}".format(task_id), exc_info=True)
        return jsonify(response), 500


##############################################################################################


"""
    Function to activate the motion agent.
"""


@app.route("/api/motion_agent/activate", methods=['POST'])
@authentication_required
def activate_motion_agent_api():
    if not check_status_motion_agent():

        motion_agent_mode = "photo"

        try:
            data = request.get_json()
        except:
            data = None

        if data is not None and 'mode' in data:
            if data['mode'] == "video":
                motion_agent_mode = "video"
        try:
            # Make a subprocess and redirect stdout
            subprocess.Popen(['python3', settings.MOTION_AGENT_PATH, motion_agent_mode], stdout=subprocess.PIPE)

            # Sleep to wait to motion agent starts
            time.sleep(1)
            if check_status_motion_agent():
                log.info("The motion agent in " + motion_agent_mode + " mode has been activated")
                return jsonify( {'status': 'The motion agent in ' + motion_agent_mode + ' mode has been activated sucessfully'})
            else:
                log.error("The motion agent could not be started", exc_info=True)
                return jsonify({'status': 'The motion agent could not be started'}), 500
        except:
            log.error("The motion agent could not be started", exc_info=True)
            return jsonify({'status': 'Error, the motion agent could not be started'}), 500
    else:
        return jsonify({'status': 'The motion agent was already activated'})


##############################################################################################


"""
    Function to deactivate the motion agent.
"""


@app.route("/api/motion_agent/deactivate", methods=['POST'])
@authentication_required
def deactivate_motion_agent_api():
    if check_status_motion_agent():
        process = os.popen('pgrep -a python | grep "motion_agent" | cut -d " " -f 1')
        pid_process = int(process.read())

        try:
            os.kill(pid_process, signal.SIGKILL)

            # Sleep to wait to streaming server stops
            time.sleep(1)
            if not check_status_streaming_server():
                log.info("Motion agent has been stopped")
                return jsonify({'status': 'The motion agent has been deactivated sucessfully'})
            else:
                log.error("The motion agent could not be stopped", exc_info=True)
                return jsonify({'status': 'The motion agent could not be stopped'}), 500
        except:
            log.error("Motion agent could not stop", exc_info=True)
            return jsonify({'status': 'Error: Motion agent could not be stopped'}), 500
        finally:
            process.close()

    else:
        return jsonify({'status': 'The motion agent was already deactivated'})


##############################################################################################


"""
    Function to check the motion agent status.
"""


@app.route("/api/motion_agent/check_status", methods=['GET'])
@authentication_required
def check_motion_agent_status_api():
    if check_status_motion_agent():
        return jsonify({'status': 'ON'})

    else:
        return jsonify({'status': 'OFF'})


##############################################################################################


""" Generates a motion alert

Returns the request status

"""


@app.route("/api/motion_agent/generate_alert", methods=['POST'])
@authentication_required
def generate_motion_alert_api():
    global motion_agent_alert
    global file_path_alert

    try:
        data = request.get_json()
    except:
        return jsonify({'status': 'Error, need credentials and video/photo file path in data request'}), 400

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


@app.route("/api/motion_agent/check_alert", methods=['GET'])
@authentication_required
def check_motion_agent_alert_api():
    global motion_agent_alert
    global file_path_alert

    if motion_agent_alert == 1:
        motion_agent_alert = 0
        return jsonify({'alert': True, 'file_path': file_path_alert})
    else:
        return jsonify({'alert': False})


##############################################################################################


"""
    Function to activate the streaming mode
"""


@app.route("/api/streaming/activate", methods=['POST'])
@authentication_required
def activate_streaming_mode_api():
    if not check_status_streaming_server():

        # Make a subprocess and redirect stdout
        try:
            subprocess.Popen(['python3', settings.STREAMING_SERVER_PATH], stdout=subprocess.PIPE)

            # Sleep to wait to streaming server starts
            time.sleep(5)
            if check_status_streaming_server():
                log.info("Streaming server has been activated")
                return jsonify({'status': 'The streaming mode has been activated sucessfully'})
            else:
                log.error("The streaming server could not be started", exc_info=True)
                return jsonify({'status': 'The streaming server could not be started'}), 500

        except:
            log.error("The streaming server could not be started", exc_info=True)
            return jsonify({'status': 'The streaming server could not be started'}), 500
    else:
        return jsonify({'status': 'The streaming mode was already activated'})


##############################################################################################

"""
    Function to deactivate the streaming mode.
"""


@app.route("/api/streaming/deactivate", methods=['POST'])
@authentication_required
def deactivate_streaming_mode_api():
    if check_status_streaming_server():
        process = os.popen('pgrep -a python | grep "streaming_server" | cut -d " " -f 1')
        pid_process = int(process.read())

        try:
            os.kill(pid_process, signal.SIGKILL)

            # Sleep to wait to streaming server stops
            time.sleep(1)
            if not check_status_streaming_server():
                log.info("Streaming server has been disconnected")
                return jsonify({'status': 'The streaming server has been stopped sucessfully'})
            else:
                log.error("The streaming server could not be stopped", exc_info=True)
                return jsonify({'status': 'The streaming server could not be stopped'}), 500
        except:
            log.error("The streaming server could not be stopped", exc_info=True)
            return jsonify({'status': 'The streaming server could not be stopped'}), 500
        finally:
            process.close()
    else:
        return jsonify({'status': 'The streaming mode was already deactivated!'})

##############################################################################################

@app.route("/api/streaming/check_status", methods=['GET'])
@authentication_required
def check_streaming_server_status_api():
    if check_status_streaming_server():
        return jsonify({'status': 'ON'})

    else:
        return jsonify({'status': 'OFF'})

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

""" 
    Asynchronous task to take a photo
"""


@celery.task(name="api_take_photo")
def take_photo(photo_path=settings.PHOTO_FILES_PATH):
    photo_config = read_photo_configuration()

    camera_photo = Photo(file_path=photo_path, resolution=photo_config['resolution'],
                         vflip=photo_config['vflip'], hflip=photo_config['hflip'])
    camera_photo.rotate(photo_config['rotation'])
    photo_file_path = camera_photo.take_photo()
    camera_photo.close()

    return photo_file_path


##############################################################################################

""" 
    Asynchronous task to record a video
"""


@celery.task(name="api_record_video")
def record_video(record_time, video_path=settings.VIDEO_FILES_PATH):
    video_config = read_video_configuration()

    video_camera = Video(file_path=video_path, showDatetime=video_config['showDatetime'],
                         resolution=video_config['resolution'], vflip=video_config['vflip'],
                         hflip=video_config['hflip'])

    video_camera.rotate(video_config['rotation'])

    # Record max long is 1 hour
    if record_time > 3600:
        record_time = 3600
    elif record_time < 0:
        record_time = 5

    video_file_path = video_camera.record_video(record_time)

    video_camera.close()

    return video_file_path


##############################################################################################

"""
    Function to check the motion agent status. True if is running, False otherwise
"""


def check_status_motion_agent():
    try:
        process = os.popen('pgrep -a python | grep "motion_agent" | cut -d " " -f1')
        pid_process = process.read()
    except:
        log.error("Error while checking motion agent status", exc_info=True)
    finally:
        process.close()

    if (pid_process != ""):
        return True
    else:
        return False


##############################################################################################

"""
    Function to check the streaming mode proccess is running. True if is running, False otherwise
"""


def check_status_streaming_server():
    try:
        process = os.popen('pgrep -a python | grep "streaming_server" | cut -d " " -f 1')
        pid_process = process.read()
    except:
        log.error("Error while checking streaming server status", exc_info=True)
    finally:
        process.close()

    if (pid_process == ""):
        return False
    else:
        return True


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
