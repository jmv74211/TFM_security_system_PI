import telebot  # Telegram API
from telebot import types  # Import to use telegram buttons
import requests, json  # Imports to make an decode requests
from time import sleep  # sleep
from functools import wraps  # Import to use decoration functions
import yaml  # Import to read the configuration file
import settings  # Import to read configuration info
from modules.logger import TelegramBotAgentLogger
import os # Joins path
import re # regex

##############################################################################################

"""
    TELEGRAM BOT: bot that receives requests and forwards them to the main agent to return the response to the telegram user.
"""

# Path where is saved the telegram configuration file.

"""
    Read configuration information
"""
with open(settings.TELEGRAM_CONFIG_PATH, 'r') as ymlfile:
    telegram_config = yaml.load(ymlfile, Loader=yaml.FullLoader)

# TOKEN API telegram. It is added in environmet vars.
TOKEN = telegram_config['telegram_bot']['api_token']

# Credentials for module login. They are added in enviroment vars.
api_agent_user = telegram_config['api_agent_credentials']['api_agent_user']
api_agent_password = telegram_config['api_agent_credentials']['api_agent_password']

# Credentials telegram authentication.
telegram_user_id = telegram_config['telegram_bot']['telegram_user_id']
telegram_username = telegram_config['telegram_bot']['telegram_username']

# Host URL and port
main_agent_host = settings.API_AGENT_IP_ADDRESS + ":" + repr(settings.API_AGENT_RUNNING_PORT)

# Bot instance
bot = telebot.TeleBot(TOKEN)

# Bot mode
mode = "manual"

# Detector
detector_status = settings.DETECTOR_AGENT_STATUS

# Time (in seconds) to make request and check if exist an alert in main agent caused by
# motion agent. It is specified in automatic mode.
time_refresh_check_alert = 1

print("Bot is running!")

##############################################################################################


"""
    Function to check if the user has permission to access, checking the message.from_user.id
    and message.from_user.username
"""


def authtentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        # White list of allowd users
        allowed_users = {'users':
                             [{'id': telegram_user_id, 'username': telegram_username},
                              ]}
        allowed = False

        message = args[0]
        user_id = message.from_user.id
        username = message.from_user.username

        for item in allowed_users['users']:
            if user_id == item['id'] and username == item['username']:
                allowed = True

        if not allowed:
            bot.send_message(message.chat.id, "You have not permission to access to this content")
            return -1

        return f(*args, **kwargs)

    return decorated


##############################################################################################

"""
    Function to get parameter arguments
"""


def extract_arg(arg):
    return arg.split()[1:]


##############################################################################################

"""
    Function to get a file time
"""


def get_file_datetime(filename):
    # Remove extension file
    data_filtered = filename.replace('.jpg', '')
    data_filtered = data_filtered.replace('.mp4', '')

    # split by separator char
    data_filtered = data_filtered.split("_")

    day = data_filtered[2][6:8]
    month = data_filtered[2][4:6]
    year = data_filtered[2][:4]

    hour = data_filtered[3][:2]
    minutes = data_filtered[3][2:4]
    seconds = data_filtered[3][4:6]

    time = "{}-{}-{}__{}:{}:{}".format(year, month, day, hour, minutes, seconds)

    return time


##############################################################################################

def check_motion_agent_status():
    payload = {'user': api_agent_user, 'password': api_agent_password}

    try:
        check_motion_agent_status_request = requests.get(main_agent_host + "/api/motion_agent/check_status", json=payload)
        check_motion_agent_status_response = check_motion_agent_status_request.json()
        motion_agent_status = check_motion_agent_status_response['status']
    except:
        logger.error(
            "[agent: telegram_bot]: Error when sending request to check motion agent status. Status code = {}"
                .format(check_motion_agent_status_request.status_code))
        motion_agent_status = None

    return motion_agent_status


##############################################################################################

"""
    Function to modify detector agent status in settings file.
"""


def update_detector_agent_status_settings_file(detector_agent_status):
    settings_file_path = os.path.join(settings.ROOT_DIR, 'settings.py')
    ok = True

    try:
        f = open(settings_file_path, mode='r')
        data = f.read()
    except:
        logger.error("[agent: telegram_bot: update_detector_agent_status_settings_file]: Could not read the settings file data")
        ok = False
    finally:
        f.close()

    if detector_agent_status:
        settings.DETECTOR_AGENT_STATUS = False
        data = re.sub(r'DETECTOR_AGENT_STATUS = (\w*)', "DETECTOR_AGENT_STATUS = False", data)
    else:
        settings.DETECTOR_AGENT_STATUS = True
        data = re.sub(r'DETECTOR_AGENT_STATUS = (\w*)', "DETECTOR_AGENT_STATUS = True", data)

    try:
        f = open(settings_file_path, mode='w')
        f.write(data)
    except:
        logger.error("[agent: telegram_bot: update_detector_agent_status_settings_file]: Could not write the settings file data")
        ok = False
    finally:
        f.close()

    return ok

##############################################################################################

def send_photo(chat_id, file_path):

    try:
        photo = open(file_path, 'rb')

        bot.send_photo(chat_id, photo)

    except:
        raise

    finally:
        photo.close()



def send_video(chat_id, file_path):
    try:
        video = open(file_path, 'rb')

        bot.send_video(chat_id, video)

    except:
        raise

    finally:
        video.close()


##############################################################################################
#                                                                                            #
#                               BOT COMMANDS HANDLERS                                        #
#                                                                                            #
##############################################################################################

"""
    Return telegram user id
"""


@bot.message_handler(commands=['id'])
def get_user_id_bot(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Your user id is {}".format(message.from_user.id))


##############################################################################################


"""
    Return telegram username
"""


@bot.message_handler(commands=['username'])
def get_username_bot(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Your username is {}".format(message.from_user.username))


##############################################################################################


"""
    Return telegram credentials
"""


@bot.message_handler(commands=['credentials'])
def get_credentials_bot(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Your user id is {} and your username is {}"
                     .format(message.from_user.id, message.from_user.username))


##############################################################################################


"""
    Take a photo and send it using /photo command
"""


@bot.message_handler(commands=['photo'])
@authtentication_required
def send_photo_bot(message):
    chat_id = message.chat.id

    payload = {'user': api_agent_user, 'password': api_agent_password}

    task_finished = False

    photo_path = ''

    try:
        take_photo_request = requests.post(main_agent_host + "/api/take_photo", json=payload)

        logger.debug("A photo has been taken...")

        photo_data_response = take_photo_request.json()

        photo_task_id = photo_data_response['task_id']

    except:

        logger.error("[agent: telegram_bot]: Error while sending take photo request with status code = {}".format(
            take_photo_request.status_code))

        bot.send_message(chat_id,
                         "Error could not take the photo. Please contact with the telegram bot administrator. Status code = {}".format(
                             take_photo_request.status_code))

    while not task_finished:
        try:
            photo_task_result_request = requests.get(main_agent_host + "/api/result/" + photo_task_id, json=payload)
            photo_task_result_response = photo_task_result_request.json()
            task_finished = photo_task_result_response['ready'] == True
        except:
            logger.error("[agent: telegram_bot]: Error while sending task result request with status code = {}".format(
                photo_task_result_request.status_code))

            bot.send_message(chat_id,
                             "Error could not send the photo. Please contact with the telegram bot administrator. Status code = {}".format(
                                 photo_task_result_request.status_code))
            return

        if task_finished:
            photo_path = photo_task_result_response['result']
        else:
            sleep(1)  # 1 seconds to send a new request

    logger.info("Photo taken at {} is being sending...".format(get_file_datetime(photo_path)))

    bot.send_message(chat_id, "Photo taken at {} is being sending...".format(get_file_datetime(photo_path)))

    try:
        send_photo(chat_id, photo_path)
        logger.debug("Photo has been sent")
    except:
        logger.error("[agent: telegram_bot]: Could not send the photo, maybe wrong photo file")
        bot.send_message(chat_id, "Sorry, could not send the photo")




############################################################################################

"""
    Record a video and send it using /video command. it can be specified a time parameter
    in seconds to recording
"""


@bot.message_handler(commands=['video'])
@authtentication_required
def send_video_bot(message):
    # Extract arguments list command
    argument_list = extract_arg(message.text)

    record_time = 10  # Default record time = 10 seconds

    chat_id = message.chat.id

    task_finished = False

    video_path = ''

    if len(argument_list) > 0:  # Means that video command has one or more parameters
        record_time = int(argument_list[0])  # Get the time parameters in seconds
        payload = {'user': api_agent_user, 'password': api_agent_password, 'recordtime': record_time}
    else:
        payload = {'user': api_agent_password, 'password': api_agent_password}

    bot.send_message(chat_id, "It is going to be recorded a video with {} seconds length".format(record_time))

    try:
        record_video_request = requests.post(main_agent_host + "/api/record_video", json=payload)

        logger.debug("A video request has been sent...")

        record_video_data_response = record_video_request.json()

        record_video_task_id = record_video_data_response['task_id']

    except:

        logger.error("[agent: telegram_bot]: Error while sending record video request with status code = {}".format(
            record_video_request.status_code))

        bot.send_message(chat_id,
                         "Error could not record the video. Please contact with the telegram bot administrator. Status code = {}".format(
                             record_video_request.status_code))

    while not task_finished:
        try:
            video_task_result_request = requests.get(main_agent_host + "/api/result/" + record_video_task_id,
                                                     json=payload)
            video_task_result_response = video_task_result_request.json()
            task_finished = video_task_result_response['ready'] == True
        except:
            logger.error("[agent: telegram_bot]: Error while sending task result request with status code = {}".format(
                video_task_result_request.status_code))

            bot.send_message(chat_id,
                             "Error could not send the video Please contact with the telegram bot administrator. Status code = {}".format(
                                 video_task_result_request.status_code))
            return

        if task_finished:
            video_path = video_task_result_response['result']
        else:
            sleep(1)  # 1 seconds to send a new request

    logger.info("Video recorded at {} is being sending...".format(get_file_datetime(video_path)))

    bot.send_message(chat_id, "Video recorded at {} seconds is being sending...".format(get_file_datetime(video_path)))

    if record_time <= 25:
        try:
            send_video(chat_id, video_path)
            logger.debug("Video has been sent")
        except:
            logger.error("[agent: telegram_bot]: Could not send the video, maybe wrong video file")
            bot.send_message(chat_id, "Sorry, could not send the video")

    else:
        bot.send_message(chat_id, "The video cannot be sent because it weights more than 50MB, but"
                         + " has been stored locally on the server.")



##############################################################################################


##############################################################################################

"""
    Enable automatic mode. It activates the motion agent and streaming server. IN addition,
    checks if exist and alert, in that case send a video o photo message.
"""


@bot.message_handler(commands=['automatic'])
@authtentication_required
def enable_automatic_mode_bot(message):
    global mode
    chat_id = message.chat.id

    motion_agent_mode = "photo"
    # Extract arguments list command
    argument_list = extract_arg(message.text)
    if len(argument_list) > 0 and argument_list[0] == "video":
        motion_agent_mode = "video"

    payload = {'user': api_agent_user, 'password': api_agent_password, 'motion_agent_mode': motion_agent_mode}

    if mode == "manual" or mode == "streaming":

        # If we are in streaming mode, we need to deactivate the streaming server
        if mode == "streaming":
            # request to deactivate the streaming server.
            try:
                deactivate_streaming_server_request = requests.post(main_agent_host + "/api/streaming/deactivate",
                                                                    json=payload)
                if deactivate_streaming_server_request.status_code == 200:  # OK
                    bot.send_message(chat_id, "Streaming mode deactivated successfully!")
                else:
                    logger.error("[agent: telegram_bot]: Error when deactivating streaming mode. Status code = {}")
                    bot.send_message(chat_id, "Error when deactivating streaming mode. Status code = {}".
                                     format(deactivate_streaming_server_request.status_code))
            except:
                logger.error("[agent: telegram_bot]: Error when deactivating streaming mode. Status code = {}")
                bot.send_message(chat_id, "Error when deactivating streaming mode. Status code = {}".
                                 format(deactivate_streaming_server_request.status_code))

        mode = "automatic"

        # request to activate the motion agent
        try:
            activate_motion_agent_request = requests.post(main_agent_host + "/api/motion_agent/activate", json=payload)

            if activate_motion_agent_request.status_code != 200:  # OK
                logger.error("[agent: telegram_bot]: Error. Motion agent can not be activated. Status code = {}") \
                    .format(activate_motion_agent_request.status_code)
                bot.send_message(chat_id, "Error. Motion agent can not be activated. Status code = {}".
                                 format(activate_motion_agent_request.status_code))

            logger.debug("Mode selected: Automatic")
            bot.send_message(chat_id, "Mode selected: Automatic")

        except:
            logger.error("[agent: telegram_bot]: Error when activating motion agent. Status code = {}"
                         .format(activate_motion_agent_request.status_code))
            bot.send_message(chat_id, " Error when activating motion agent. Status code = {}".
                             format(activate_motion_agent_request.status_code))
    else:
        logger.debug("You are already in automatic mode")
        bot.send_message(chat_id, "You are already in automatic mode")

    while mode == "automatic":
        # request to check if there is a motion agent alert
        file_path = ''
        try:
            check_motion_agent_request = requests.get(main_agent_host + "/api/motion_agent/check_alert", json=payload)

            check_motion_agent_data_response = check_motion_agent_request.json()

            alert = check_motion_agent_data_response['alert']
        except:
            logger.error("[agent: telegram_bot]: Error api agent does not response. Status code = {}".
                         format(check_motion_agent_request.status_code))
            bot.send_message(chat_id,
                             "Error, API agent does not response and automatic mode could not be enabled. Status code = {} "
                             .format(check_motion_agent_request.status_code))
            return

        if alert == True:
            logger.debug("ALERT!")

            try:
                file_path = check_motion_agent_data_response['file_path']
            except:
                logger.error("[agent: telegram_bot]: Error, could not read file path from api agent alert")
                return

            if motion_agent_mode == "photo":
                try:
                    send_photo(chat_id, file_path)
                except:
                    logger.error("[agent: telegram_bot]: Could not send the photo, maybe wrong photo file")
                    bot.send_message(chat_id, "Sorry, could not send the photo alert")
            else: # Video mode
                send_video(chat_id, file_path)

        sleep(time_refresh_check_alert)


##############################################################################################

"""
    Enable manual mode. It deactivates the motion agent or streaming server.
"""


@bot.message_handler(commands=['manual'])
@authtentication_required
def enable_manual_mode_bot(message):
    global mode
    chat_id = message.chat.id
    payload = {'user': api_agent_user, 'password': api_agent_password}

    if mode == "automatic" or mode == "streaming":

        if mode == "streaming":
            # request to deactivate the streaming server.
            try:
                deactivate_streaming_server_request = requests.post(main_agent_host + "/api/streaming/deactivate",
                                                                    json=payload)
                if deactivate_streaming_server_request.status_code == 200:  # OK
                    bot.send_message(chat_id, "Streaming mode deactivated successfully!")
                else:
                    bot.send_message(chat_id, "Error: Streaming mode can not be deactivated")
            except:
                logger.error("[agent: telegram_bot]: Error when deactivating streaming server. Status code = {}"
                             .format(deactivate_streaming_server_request.status_code))
                bot.send_message(chat_id, " Error when deactivating streaming server. Status code = {}".
                                 format(deactivate_streaming_server_request.status_code))

        elif mode == "automatic":
            # request to deactivate the motion agent.
            try:
                deactivate_motion_agent_request = requests.post(main_agent_host + "/api/motion_agent/deactivate",
                                                                json=payload)
                if deactivate_motion_agent_request.status_code == 200:  # OK
                    bot.send_message(chat_id, "Automatic mode deactivated successfully!")
                else:
                    logger.error("[agent: telegram_bot]: Error, automatic mode can not be deactivated. Status code = {}"
                                 .format(deactivate_motion_agent_request.status_code))
                    bot.send_message(chat_id, "Error: Automatic mode can not be deactivated. Status code = {}".
                                     format(deactivate_motion_agent_request.status_code))
            except:
                logger.error("[agent: telegram_bot]: Error when deactivating motion agent. Status code = {}"
                             .format(deactivate_motion_agent_request.status_code))
                bot.send_message(chat_id, " Error when deactivating motion agent. Status code = {}".
                                 format(deactivate_motion_agent_request.status_code))
        mode = "manual"
        logger.debug("Mode selected: Manual")
        bot.send_message(chat_id, "Mode selected: Manual")
    else:
        bot.send_message(chat_id, "You are already in manual mode!")


##############################################################################################

"""
    Enable streaming mode. It deactivates the motion agent.
"""


@bot.message_handler(commands=['streaming'])
@authtentication_required
def enable_streaming_mode_bot(message):
    global mode
    chat_id = message.chat.id
    payload = {'user': api_agent_user, 'password': api_agent_password}

    if mode == "automatic" or mode == "manual":

        if mode == "automatic":
            # request to deactivate the motion agent.
            try:
                deactivate_motion_agent_request = requests.post(main_agent_host + "/api/motion_agent/deactivate",
                                                                json=payload)
                if deactivate_motion_agent_request.status_code == 200:  # OK
                    bot.send_message(chat_id, "Automatic mode deactivated successfully!")
                else:
                    logger.error("[agent: telegram_bot]: Error when deactivating motion agent. Status code = {}"
                                 .format(deactivate_motion_agent_request.status_code))
                    bot.send_message(chat_id, "Error: Automatic mode can not be deactivated. Status code = {}"
                                     .format(deactivate_motion_agent_request.status_code))
            except:
                logger.error(
                    "[agent: telegram_bot]: Error when sending request to deactivate motion agent. Status code = {}"
                        .format(deactivate_motion_agent_request.status_code))
                bot.send_message(chat_id, "Error: Automatic mode can not be deactivated. Status code = {}"
                                 .format(deactivate_motion_agent_request.status_code))

        mode = "streaming"

        try:
            activate_streaming_server_request = requests.post(main_agent_host + "/api/streaming/activate", json=payload)
            if activate_streaming_server_request.status_code == 200:  # OK
                streaming = settings.STREAMING_SERVER_IP_ADDRESS + ":" + repr(settings.STREAMING_SERVER_PORT)
                bot.send_message(chat_id, "Mode selected: Streaming. Watch it here --> " + streaming)
                logger.debug("Mode selected: Streaming")
            else:
                bot.send_message(chat_id, "Error: Streaming mode can not be deactivated. Status code = {}"
                                 .format(activate_streaming_server_request.status_code))
                logger.error(
                    "[agent: telegram_bot]: Error when sending request to activate streaming server. Status code = {}"
                        .format(activate_streaming_server_request.status_code))
                bot.send_message(chat_id, "Error: Automatic mode can not be deactivated. Status code = {}"
                                 .format(activate_streaming_server_request.status_code))
        except:
            logger.error(
                "[agent: telegram_bot]: Error when sending request to activate streaming server. Status code = {}"
                    .format(activate_streaming_server_request.status_code))
            bot.send_message(chat_id, "Error: streaming mode can not be deactivated. Status code = {}"
                             .format(activate_streaming_server_request.status_code))
    elif mode == "streaming":
        streaming = settings.STREAMING_SERVER_IP_ADDRESS + ":" + repr(settings.STREAMING_SERVER_PORT)
        bot.send_message(chat_id, "You are already in streaming mode.  Watch it here --> " + streaming)


##############################################################################################

"""
    Get the current mode.
"""


@bot.message_handler(commands=['gmode'])
@authtentication_required
def get_mode_bot(message):
    chat_id = message.chat.id
    if mode == "automatic":
        bot.send_message(chat_id, "Current mode: Automatic")
    elif mode == "streaming":
        bot.send_message(chat_id, "Current mode: Streaming")
    else:
        bot.send_message(chat_id, "Current mode: Manual")


##############################################################################################

"""
    Activate detector agent mode in motion agent.
"""


@bot.message_handler(commands=['detector'])
@authtentication_required
def toogle_detector_bot(message):
    global detector_status
    chat_id = message.chat.id
    detector_status = settings.DETECTOR_AGENT_STATUS

    # Toogle value: True --> False, False --> True
    update_detector_agent_status_settings_file(detector_status)

    # Check if the file has been updated successfully
    if(detector_status == settings.DETECTOR_AGENT_STATUS):
        logger.error("[agent: telegram_bot]: Error, could not update the detector agent status")
        bot.send_message(chat_id, "Error, could not update the detector agent status")
        return

    # Check motion agent status
    motion_agent_status = check_motion_agent_status()

    if settings.DETECTOR_AGENT_STATUS: #Activated
        logger.info("Detector agent has been enabled")
        bot.send_message(chat_id, "Detector agent has been enabled. ")

    else: # Deactivated
        logger.info("Detector agent has been disabled")
        bot.send_message(chat_id, "Detector agent has been disabled")

    if motion_agent_status == 'ON':
        bot.send_message(chat_id, "You must disable and enable automatic mode for the changes to take effect")

#
# ##############################################################################################
#



logger = TelegramBotAgentLogger()

# bot running
bot.polling(none_stop=True)
