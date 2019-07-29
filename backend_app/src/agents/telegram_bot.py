import telebot  # Telegram API
from telebot import types  # Import to use telegram buttons
import requests, json  # Imports to make an decode requests
from time import sleep            # sleep
from functools import wraps  # Import to use decoration functions
import yaml  # Import to read the configuration file
import settings  # Import to read configuration info
from modules.logger import TelegramBotAgentLogger

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

    time = "{}-{}-{}__{}:{}:{}".format(year,month,day,hour, minutes, seconds)

    return time


##############################################################################################

##############################################################################################


"""
    Take a photo and send it using /photo command
"""


@bot.message_handler(commands=['photo'])
@authtentication_required
def send_photo(message):

    print("ENTRO")

    chat_id = message.chat.id

    payload = {'user': api_agent_user, 'password': api_agent_password}

    task_finished = False

    photo_path = ''

    try:
        take_photo_request = requests.post(main_agent_host + "/api/take_photo", json=payload)

        logger.debug("A photo has been taken...")

        photo_data_response =  take_photo_request.json()

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

    photo = open(photo_path, 'rb')

    bot.send_photo(chat_id, photo)

    photo.close()

    logger.debug("Photo has been sent")

############################################################################################

"""
    Record a video and send it using /video command. it can be specified a time parameter
    in seconds to recording
"""


@bot.message_handler(commands=['video'])
@authtentication_required
def send_video(message):
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

        record_video_data_response =  record_video_request.json()

        record_video_task_id = record_video_data_response['task_id']

    except:

        logger.error("[agent: telegram_bot]: Error while sending record video request with status code = {}".format(
            record_video_request.status_code))

        bot.send_message(chat_id,
                         "Error could not record the video. Please contact with the telegram bot administrator. Status code = {}".format(
                             record_video_request.status_code))

    while not task_finished:
        try:
            video_task_result_request = requests.get(main_agent_host + "/api/result/" + record_video_task_id, json=payload)
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

    video = open(video_path, 'rb')

    if record_time <= 25:
        bot.send_video(chat_id, video)
    else:
        bot.send_message(chat_id, "The video cannot be sent because it weights more than 50MB, but"
                         + " has been stored locally on the server.")

    video.close()

    logger.debug("Video has been sent")

##############################################################################################


##############################################################################################

"""
    Enable automatic mode. It activates the motion agent and streaming server. IN addition,
    checks if exist and alert, in that case send a video o photo message.
"""


@bot.message_handler(commands=['automatic'])
@authtentication_required
def enable_automatic_mode(message):
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
                logger.error("[agent: telegram_bot]: Error. Motion agent can not be activated. Status code = {}")\
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

        print("Estoy")
        check_motion_agent_request = requests.get(main_agent_host + "/api/motion_agent/check_alert", json=payload)

        check_motion_agent_data_response = check_motion_agent_request.json()

        alert = check_motion_agent_data_response['alert']

        print(repr(check_motion_agent_data_response))
        print(check_motion_agent_request.status_code)

        if alert == True:
            logger.debug("ALERT!")
            if motion_agent_mode == "photo":
                send_photo(message)
            else:
                send_video(message)

        sleep(time_refresh_check_alert)

##############################################################################################

"""
    Enable manual mode. It deactivates the motion agent or streaming server.
"""


@bot.message_handler(commands=['manual'])
@authtentication_required
def enable_manual_mode(message):
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
                deactivate_motion_agent_request = requests.post(main_agent_host + "/api/motion_agent/deactivate", json=payload)
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





logger = TelegramBotAgentLogger()

# bot running
bot.polling(none_stop=True)
