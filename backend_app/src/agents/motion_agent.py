import RPi.GPIO as GPIO
from time import sleep
import requests
import settings
import yaml
import sys
import time
from modules.photo import Photo
from modules.video import Video
from agents.api_agent import read_photo_configuration, read_video_configuration
from modules.logger import MotionAgentLogger

##############################################################################################

"""
    MOTION AGENT: Captures sensor movement, takes a photo/video and sends an alert to main agent.
    
    The motion agent functionality is:
     1. Dectect a sensor movement
     2. Take a video/picture
     3. Send a request with file_path data to generate and alert in API agent

"""

with open(settings.CONFIG_FILE_AUTHENTICATION, 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# Main agent host
main_agent_host = settings.API_AGENT_IP_ADDRESS + ":{}".format(settings.API_AGENT_RUNNING_PORT)

# Detector agent
detector_agent_host = settings.DETECTOR_AGENT_IP_ADDRESS + ":{}".format(settings.DETECTOR_AGENT_RUNNING_PORT)

user = cfg['authentication']['user']
password = settings.API_PASSWORD

# Set pin recognition.The other method is #GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)

pin_number = settings.GPIO_SENSOR_PIN_NUMBER

# Set pin mode as input
GPIO.setup(pin_number, GPIO.IN)

activate_time = 0.5

# Motion_agent_mode
motion_agent_mode = "photo"

# Logger
logger = MotionAgentLogger()

##############################################################################################

def detect_person(objects):
    person_detected = False;
    list_objects = objects['objects']

    for item in list_objects:
        for key, value in item.items():
            if key == 'person':
                person_detected = True

    return person_detected

##############################################################################################

if __name__ == "__main__":

    print("Motion agent is running")

    # If program has a video parameter
    if len(sys.argv) > 1 and sys.argv[1] == "video":
        motion_agent_mode = "video"

    while True:

        sleep(activate_time)
        if GPIO.input(pin_number):
            logger.info("ALERT FROM MOTION AGENT")

            if motion_agent_mode == "photo":
                photo_config = read_photo_configuration()

                camera_photo = Photo(file_path=settings.ALERTS_FILES_PATH, resolution=photo_config['resolution'],
                                     vflip=photo_config['vflip'], hflip=photo_config['hflip'])
                camera_photo.rotate(photo_config['rotation'])
                file_path = camera_photo.take_photo()
                camera_photo.close()
            else:
                video_config = read_video_configuration()

                video_camera = Video(file_path=settings.ALERTS_FILES_PATH, showDatetime=video_config['showDatetime'],
                                     resolution=video_config['resolution'], vflip=video_config['vflip'],
                                     hflip=video_config['hflip'])
                video_camera.rotate(video_config['rotation'])

                file_path = video_camera.record_video(record_time=15)
                video_camera.close()

            payload = {'user': user, 'password': password, 'file_path': file_path}
            headers = {'content-type': 'application/json'}

            # If detector agent is enabled, filter the image and generate an alert if there is a person in the photo
            if settings.DETECTOR_AGENT_STATUS:

                try:
                    logger.debug("Sending a request to detector agent")
                    start_time = time.time()
                    req = requests.get(detector_agent_host + "/api/detector", json=payload, headers=headers)
                    detector_time = time.time() - start_time
                    logger.info("Detector request sent, and it has been responsed in = {} seconds".format(detector_time))
                except:
                    logger.error(
                        "Error while trying to send an alert to Detector API agent with address {}.¿It is running?".format(
                            detector_agent_host))

                person_detected = detect_person(req.json())

                logger.info("Person detected = {}".format(person_detected))
            # If detector agent is disabled, generate an alert
            else:
                try:
                    motion_agent_request = requests.post(main_agent_host + "/api/motion_agent/generate_alert", json=payload,
                                                         headers=headers)
                except:
                    logger.error("Error while trying to send an alert to API agent with address {}.¿It is running?".format(
                        main_agent_host))

            sleep(settings.REFRESH_TIME)

