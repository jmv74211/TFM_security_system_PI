import telebot  # Telegram API
import requests, json  # Imports to make an decode requests
from time import sleep  # sleep
from functools import wraps  # Import to use decoration functions
import yaml  # Import to read the configuration file
import os  # Joins path
import re  # regex
from modules.logger import TelegramBotAgentLogger
import settings  # Import to read configuration info
from telebot import types

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
bot_user_id = telegram_config['telegram_bot']['bot_user_id']
bot_username = telegram_config['telegram_bot']['bot_username']

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

##############################################################################################
#                                                                                            #
#                               SUPPORT API FUNCTIONS                                        #
#                                                                                            #
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
                             [{'id': telegram_user_id, 'username': telegram_username},  # Your username and user id
                              {'id': bot_user_id, 'username': bot_username},  # Telegram bot user and user id
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
    Function to check if the api agent and/or object detector agent services is running. 
"""


def services_are_running(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if isinstance(args[0], telebot.types.CallbackQuery):
            chat_id = args[0].message.chat.id
        else: # message instance
            chat_id = args[0].chat.id

        api_agent_address = "{}:{}".format(settings.API_AGENT_IP_ADDRESS, settings.API_AGENT_RUNNING_PORT)
        api_agent_url = os.path.join(api_agent_address, "api", "echo")

        try:
            requests.get(api_agent_url)
        except:
            bot.send_message(chat_id, "\u274C API agent is off. Please activate the service in your server to use the bot" )
            return -1

        if settings.DETECTOR_AGENT_STATUS:

            object_detector_agent_address = "{}:{}".format(settings.DETECTOR_AGENT_IP_ADDRESS, settings.DETECTOR_AGENT_RUNNING_PORT)
            object_detector_agent_url = os.path.join(object_detector_agent_address, "api", "echo")

            try:
                requests.get(object_detector_agent_url)
            except:
                bot.send_message(chat_id, "\u274C Object detector agent is off and is enabled in the configuration. "
                                                  "Please activate the agent service in your server or deactivate it "
                                                  "in \u2B50 Mode -> \u2B55 Toggle detector status")
            return -1

        return f(*args, **kwargs)

    return decorated


##############################################################################################

""" Function to get parameter arguments

Returns arguments list.

"""


def extract_arg(arg):
    return arg.split()[1:]


##############################################################################################

""" Function to get a file time

Returns:  Datetime info. Example: (2019-07-30__11:04:21)

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

""" 
    Function to send a photo to telegram chat
"""


def send_photo(chat_id, file_path):
    try:
        photo = open(file_path, 'rb')

        bot.send_photo(chat_id, photo)

    except:
        raise

    finally:
        photo.close()


##############################################################################################

""" 
    Function to send a video to telegram chat
"""


def send_video(chat_id, file_path):
    try:
        video = open(file_path, 'rb')

        bot.send_video(chat_id, video)

    except:
        raise

    finally:
        video.close()


##############################################################################################

""" 
    Function to activate streaming server
"""


def activate_streaming_server():
    payload = {'user': api_agent_user, 'password': api_agent_password}

    try:
        deactivate_streaming_server_request = requests.post(main_agent_host + "/api/streaming/activate", json=payload)
        if deactivate_streaming_server_request.status_code != 200:  # OK
            raise
        logger.debug("Streaming server activated successfully")
    except:
        logger.error("[agent: telegram_bot]: Error when activating streaming mode.")
        raise


#############################################################################################

""" 
    Function to deactivate streaming server
"""


def deactivate_streaming_server():
    payload = {'user': api_agent_user, 'password': api_agent_password}

    try:
        deactivate_streaming_server_request = requests.post(main_agent_host + "/api/streaming/deactivate", json=payload)

        if deactivate_streaming_server_request.status_code != 200:  # OK
            raise
        logger.debug("Streaming server deactivated successfully")
    except:
        logger.error("[agent: telegram_bot]: Error when deactivating streaming mode.")
        raise


##############################################################################################

""" 
    Function to activate motion agent
"""


def activate_motion_agent():
    payload = {'user': api_agent_user, 'password': api_agent_password}

    try:
        activate_motion_agent_request = requests.post(main_agent_host + "/api/motion_agent/activate", json=payload)
        if activate_motion_agent_request.status_code != 200:  # OK
            raise
        logger.debug("Motion agent activated successfully")
    except:
        logger.error("[agent: telegram_bot]: Error when activating motion agent.")
        raise


##############################################################################################

""" 
    Function to deactivate motion agent
"""


def deactivate_motion_agent():
    payload = {'user': api_agent_user, 'password': api_agent_password}

    try:
        deactivate_motion_agent_request = requests.post(main_agent_host + "/api/motion_agent/deactivate", json=payload)
        if deactivate_motion_agent_request.status_code != 200:  # OK
            raise
        logger.debug("Motion agent deactivated successfully")
    except:
        logger.error("[agent: telegram_bot]: Error when deactivating motion agent.")
        raise


##############################################################################################

""" Function to check if there is an alert in api agent.
    
Returns: Tuple with alert value and file path. If there is not an alert, then will returns (False, ''), 
otherwise will returns (True,'/home/...')

"""


def check_api_agent_alert():
    payload = {'user': api_agent_user, 'password': api_agent_password}

    file_path = ''

    try:
        check_motion_agent_request = requests.get(main_agent_host + "/api/motion_agent/check_alert", json=payload)

        check_motion_agent_data_response = check_motion_agent_request.json()

        alert = check_motion_agent_data_response['alert']

        if alert:
            try:
                file_path = check_motion_agent_data_response['file_path']
                logger.debug("A motion agent alert has occurred with file path: {}".format(file_path))
            except:
                logger.error(
                    "[agent: telegram_bot]: Error could not read file path data from api agent alert.")
                raise

    except:
        logger.error("[agent: telegram_bot]: Error when checking api agent alert.")
        raise

    return (alert, file_path)


##############################################################################################

""" Function to check the motion agent status

Returns: True if it is enabled, False if not and None if a error has occurred.  

"""


def check_motion_agent_status():
    payload = {'user': api_agent_user, 'password': api_agent_password}

    try:
        check_motion_agent_status_request = requests.get(main_agent_host + "/api/motion_agent/check_status",
                                                         json=payload)
        check_motion_agent_status_response = check_motion_agent_status_request.json()
        motion_agent_status = check_motion_agent_status_response['status']
    except:
        logger.error(
            "[agent: telegram_bot]: Error when sending request to check motion agent status.")
        motion_agent_status = None

    return motion_agent_status


##############################################################################################

""" Function to modify detector agent status in settings file.

Returns: True if it has been updated successfully, False otherwise.

"""


def update_detector_agent_status_settings_file(detector_agent_status):
    settings_file_path = os.path.join(settings.ROOT_DIR, 'settings.py')
    ok = True

    try:
        f = open(settings_file_path, mode='r')
        data = f.read()
    except:
        logger.error(
            "[agent: telegram_bot: update_detector_agent_status_settings_file]: Could not read the settings file data")
        ok = False
    finally:
        f.close()

    # REGEX to update detector agent status in settings file
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
        logger.error(
            "[agent: telegram_bot: update_detector_agent_status_settings_file]: Could not write the settings file data")
        ok = False
    finally:
        f.close()

    return ok


##############################################################################################

""" Function to obtain a specific parameter in a module configuration

Returns: Configuration module parameter value

"""


def get_module_parameter_configuration(module, parameter):
    with open(settings.CONFIG_FILE_MODULE_PATH, 'r') as ymlfile:
        module_config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    try:
        value = module_config[module][parameter]
    except:
        logger.error("[agent: telegram_bot]: Error, could not read module config [{}][{}]".format(module, parameter))
        raise
    return value


##############################################################################################

""" Function to obtain the module configuration parameters

Returns: Dict with module configuration value

"""


def get_module_configuration(module):
    with open(settings.CONFIG_FILE_MODULE_PATH, 'r') as ymlfile:
        module_config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    try:
        map_result = dict()
        for parameter in module_config[module]:
            map_result[parameter] = module_config[module][parameter]
    except:
        logger.error("[agent: telegram_bot]: Error, could not read module config [{}]".format(module))
        raise

    return map_result


##############################################################################################

""" 
    Function to update the module configuration parameters.
"""


def set_module_parameter_configuration(module, parameter, value):
    with open(settings.CONFIG_FILE_MODULE_PATH, 'r') as ymlfile:
        module_config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    try:
        module_config[module][parameter] = value

        with open(settings.CONFIG_FILE_MODULE_PATH, "w") as ymlfile:
            yaml.dump(module_config, ymlfile)
    except:
        logger.error(
            "[agent: telegram_bot]: Error, could not write in module config [{}][{}] = {}".format(module, parameter,
                                                                                                  value))
        raise


##############################################################################################

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
@services_are_running
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

        logger.error("[agent: telegram_bot]: Error while sending take photo request")

        bot.send_message(chat_id,
                         "Error could not take the photo. Please contact with the telegram bot administrator.")
        return

    while not task_finished:
        try:
            photo_task_result_request = requests.get(main_agent_host + "/api/result/" + photo_task_id, json=payload)
            photo_task_result_response = photo_task_result_request.json()
            task_finished = photo_task_result_response['ready'] == True
        except:
            logger.error("[agent: telegram_bot]: Error while sending task result request")

            bot.send_message(chat_id,
                             "Error could not send the photo. Please contact with the telegram bot administrator.")
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
        return


############################################################################################

"""
    Record a video and send it using /video command. it can be specified a time parameter
    in seconds to recording
"""


@bot.message_handler(commands=['video'])
@services_are_running
@authtentication_required
def send_video_bot(message, record_time=10):
    # Extract arguments list command
    argument_list = extract_arg(message.text)

    chat_id = message.chat.id

    task_finished = False

    video_path = ''

    if len(argument_list) > 0 and argument_list[0].isdigit():  # Means that video command has one or more parameters
        record_time = int(argument_list[0])  # Get the time parameters in seconds
        payload = {'user': api_agent_user, 'password': api_agent_password, 'recordtime': record_time}
    else:
        payload = {'user': api_agent_user, 'password': api_agent_password}

    bot.send_message(chat_id, "It is going to be recorded a video with {} seconds length".format(record_time))

    # Record video request
    try:
        record_video_request = requests.post(main_agent_host + "/api/record_video", json=payload)

        logger.debug("A video request has been sent...")

        record_video_data_response = record_video_request.json()

        record_video_task_id = record_video_data_response['task_id']

    except:

        logger.error("[agent: telegram_bot]: Error while sending record video request")

        bot.send_message(chat_id,
                         "Error could not record the video. Please contact with the telegram bot administrator.")
        return

    # Wait until the asynchronous task is finished
    while not task_finished:
        try:
            video_task_result_request = requests.get(main_agent_host + "/api/result/" + record_video_task_id,
                                                     json=payload)
            video_task_result_response = video_task_result_request.json()
            task_finished = video_task_result_response['ready'] == True
        except:
            logger.error("[agent: telegram_bot]: Error while sending task result request")

            bot.send_message(chat_id,
                             "Error could not send the video Please contact with the telegram bot administrator.")
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
            return

    else:
        bot.send_message(chat_id, "The video cannot be sent because it weights more than 50MB, but"
                         + " has been stored locally on the server.")


##############################################################################################

"""
    Enable automatic mode. It activates the motion agent and stops streaming or manual mode (If any are currently activated).
     In addition, checks if exist and alert, in that case send a video o photo message filtered by object detector agent
    (if its status is enabled in settings file configuration through /detector bot command or editing manually
    the detector agent status in settings file).
"""


@bot.message_handler(commands=['automatic'])
@services_are_running
@authtentication_required
def enable_automatic_mode_bot(message, motion_agent_mode="photo"):
    global mode
    chat_id = message.chat.id

    # Extract arguments list command
    argument_list = extract_arg(message.text)
    if len(argument_list) > 0 and argument_list[0] == "video":
        motion_agent_mode = "video"

    if mode == "manual" or mode == "streaming":

        # If we are in streaming mode, we need to deactivate the streaming server
        if mode == "streaming":
            # request to deactivate the streaming server.
            try:
                deactivate_streaming_server()
                bot.send_message(chat_id, "Streaming mode deactivated successfully!")
            except:
                bot.send_message(chat_id, "Error: could not deactivate streaming server")
                return

        mode = "automatic"

        # request to activate the motion agent
        try:
            activate_motion_agent()
            bot.send_message(chat_id, "Mode selected: Automatic")
        except:
            bot.send_message(chat_id, "Error: could not activate automatic mode")
            return

    while mode == "automatic":
        # request to check if there is a motion agent alert
        try:
            # Tuple
            alert, file_path = check_api_agent_alert()  # TENGO QUE GUARDAR TAMBIÉN FILE_PATH DE LA ALERTA
        except:
            bot.send_message(chat_id, "Error, could not check if there is an alert in api agent")
            return

        # If alert is true, then send photo or video file
        if alert == True:

            if motion_agent_mode == "photo":
                try:
                    bot.send_message(chat_id, "Alert at {}, sending photo...".format(get_file_datetime(file_path)))
                    send_photo(chat_id, file_path)
                except:
                    logger.error("[agent: telegram_bot]: Could not send the photo, maybe wrong photo file")
                    bot.send_message(chat_id, "Sorry, could not send the photo alert")
            else:  # Video mode
                try:
                    bot.send_message(chat_id, "Alert at {}, sending photo...").format(get_file_datetime(file_path))
                    send_video(chat_id, file_path)
                except:
                    logger.error("[agent: telegram_bot]: Could not send the video, maybe wrong video file")
                    bot.send_message(chat_id, "Sorry, could not send the video alert")

        # Waiting time to check the alert again
        sleep(time_refresh_check_alert)


##############################################################################################

"""
    Enable manual mode. It deactivates streaming or automatic mode (If any are currently activated).
"""


@bot.message_handler(commands=['manual'])
@services_are_running
@authtentication_required
def enable_manual_mode_bot(message):
    global mode
    chat_id = message.chat.id

    if mode == "automatic" or mode == "streaming":

        if mode == "streaming":

            # If we are in streaming mode, we need to deactivate the streaming server
            if mode == "streaming":
                # request to deactivate the streaming server.
                try:
                    deactivate_streaming_server()
                    bot.send_message(chat_id, "Streaming mode deactivated successfully!")
                except:
                    bot.send_message(chat_id, "Error: could not deactivate streaming server")
                    return

        elif mode == "automatic":
            # request to deactivate the motion agent.
            try:
                deactivate_motion_agent()
                bot.send_message(chat_id, "Automatic mode deactivated successfully!")
            except:
                bot.send_message(chat_id, "Error: could not deactivate automatic mode (motion agent)")
                return

        mode = "manual"
        logger.debug("Mode selected: Manual")
        bot.send_message(chat_id, "Mode selected: Manual")


##############################################################################################

"""
    Enable streaming mode. It deactivates manual or automatic mode (If any are currently activated).
"""


@bot.message_handler(commands=['streaming'])
@services_are_running
@authtentication_required
def enable_streaming_mode_bot(message):
    global mode
    chat_id = message.chat.id

    if mode == "automatic" or mode == "manual":

        if mode == "automatic":
            # request to deactivate the motion agent.
            try:
                deactivate_motion_agent()
                bot.send_message(chat_id, "Automatic mode deactivated successfully!")
            except:
                bot.send_message(chat_id, "Error: could not deactivate automatic mode (motion agent)")
                return

        mode = "streaming"

        # request to deactivate the motion agent.
        try:
            activate_streaming_server()
            streaming_url = settings.STREAMING_SERVER_IP_ADDRESS + ":" + repr(settings.STREAMING_SERVER_PORT)
            bot.send_message(chat_id, "Mode selected: Streaming. Watch it here --> " + streaming_url)
        except:
            bot.send_message(chat_id, "Error: Streaming mode could not be deactivated (streaming server)")
            return


##############################################################################################

"""
    Get the current mode.
"""


@bot.message_handler(commands=['gmode'])
@services_are_running
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
    Activate/Deactivate detector agent mode in motion agent.
"""


@bot.message_handler(commands=['detector'])
@authtentication_required
def toogle_detector_bot(message):
    global detector_status
    chat_id = message.chat.id
    detector_status = settings.DETECTOR_AGENT_STATUS

    # Toogle detector agent status value in settings file: True --> False, False --> True
    update_detector_agent_status_settings_file(detector_status)

    # Check if the file has been updated successfully
    if (detector_status == settings.DETECTOR_AGENT_STATUS):
        logger.error("[agent: telegram_bot]: Error, could not update the detector agent status")
        bot.send_message(chat_id, "Error, could not update the detector agent status")
        return

    # Check motion agent status
    motion_agent_status = check_motion_agent_status()

    if settings.DETECTOR_AGENT_STATUS:  # Activated
        logger.info("Detector agent has been enabled")
        bot.send_message(chat_id, "Detector agent has been enabled. ")

    else:  # Deactivated
        logger.info("Detector agent has been disabled")
        bot.send_message(chat_id, "Detector agent has been disabled")

    if motion_agent_status == 'ON':
        bot.send_message(chat_id, "You must disable and enable automatic mode for the changes to take effect")


##############################################################################################

"""
    Get current detector agent status
"""


@bot.message_handler(commands=['gdetector'])
@services_are_running
@authtentication_required
def get_detector_status_bot(message):
    chat_id = message.chat.id
    if settings.DETECTOR_AGENT_STATUS:
        bot.send_message(chat_id, "Detector is enabled")
    else:
        bot.send_message(chat_id, "Detector is disabled")


##############################################################################################

"""
    Start user interface
"""


@bot.message_handler(commands=['start'])
def start_keyboard(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "\U0001F4CC Dashboard: Choose one option:", reply_markup=inline_start_keyboard)

##############################################################################################

"""
    Start user interface starting with any character button
"""


@bot.message_handler(regexp="^[a-z,A-Z]")
def start_keyboard(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "\U0001F4CC Dashboard: Choose one option:", reply_markup=inline_start_keyboard)

##############################################################################################

######################################  START BOT INTERFACE  #################################

##############################################################################################
#                                                                                            #
#                                    BOT INLINE KEYBOARD                                     #
#                                                                                            #
##############################################################################################

###############################     MODE KEYBOARD  ##########################################

inline_start_keyboard = types.InlineKeyboardMarkup()
inline_start_keyboard_btn1 = types.InlineKeyboardButton("\u2B50 Mode", callback_data="mode_keyboard")
inline_start_keyboard_btn2 = types.InlineKeyboardButton("\U0001F527 Configuration",
                                                        callback_data="configuration_keyboard")
inline_start_keyboard_btn3 = types.InlineKeyboardButton("\U0001F4BB Commands", callback_data="commands_keyboard")
inline_start_keyboard_btn4 = types.InlineKeyboardButton("\U0001F4C4 Go to documentation",
                                                        url="https://github.com/jmv74211/TFM_security_system_PI")

inline_start_keyboard.row(inline_start_keyboard_btn1, inline_start_keyboard_btn2)
inline_start_keyboard.row(inline_start_keyboard_btn3, inline_start_keyboard_btn4)

###############################     MODE KEYBOARD  ##########################################

inline_mode_keyboard = types.InlineKeyboardMarkup()
inline_mode_keyboard_btn1 = types.InlineKeyboardButton("\U0001F446 Manual", callback_data="manual_keyboard")
inline_mode_keyboard_btn2 = types.InlineKeyboardButton("\U0001F4F2 Automatic", callback_data="automatic_keyboard")
inline_mode_keyboard_btn3 = types.InlineKeyboardButton("\U0001F4BB Streaming", callback_data="streaming_keyboard")
inline_mode_keyboard_btn4 = types.InlineKeyboardButton("\u27A1 Get current mode", callback_data="get_mode_keyboard")
inline_mode_keyboard_btn5 = types.InlineKeyboardButton("\u2B55 Toggle detector status",
                                                       callback_data="toggle_detector_status_keyboard")
inline_mode_keyboard_btn6 = types.InlineKeyboardButton("\u2733 Get detector status",
                                                       callback_data="get_detector_status_keyboard")

inline_mode_keyboard.row(inline_mode_keyboard_btn1, inline_mode_keyboard_btn2, inline_mode_keyboard_btn3)
inline_mode_keyboard.row(inline_mode_keyboard_btn4)
inline_mode_keyboard.row(inline_mode_keyboard_btn5, inline_mode_keyboard_btn6)

###############################     CONFIGURATION KEYBOARD  #################################

inline_configuration_keyboard = types.InlineKeyboardMarkup()
inline_configuration_keyboard_btn1 = types.InlineKeyboardButton("\U0001F4F7 Photo", callback_data="configuration_photo_keyboard")
inline_configuration_keyboard_btn2 = types.InlineKeyboardButton("\U0001F4F9 Video", callback_data="configuration_video_keyboard")

inline_configuration_keyboard.row(inline_configuration_keyboard_btn1, inline_configuration_keyboard_btn2)

###############################     AUTOMATIC KEYBOARD  #################################

inline_automatic_keyboard = types.InlineKeyboardMarkup()
inline_automatic_keyboard_btn1 = types.InlineKeyboardButton("\U0001F4F7 Photo", callback_data="automatic_photo_keyboard")
inline_automatic_keyboard_btn2 = types.InlineKeyboardButton("\U0001F4F9 Video", callback_data="automatic_video_keyboard")

inline_automatic_keyboard.row(inline_automatic_keyboard_btn1, inline_automatic_keyboard_btn2)

###############################     MANUAL KEYBOARD  #################################

inline_manual_keyboard = types.InlineKeyboardMarkup()
inline_manual_keyboard_btn1 = types.InlineKeyboardButton("\U0001F4F7 Take photo", callback_data="manual_photo_keyboard")
inline_manual_keyboard_btn2 = types.InlineKeyboardButton("\U0001F4F9 Record video", callback_data="manual_video_keyboard")

inline_manual_keyboard.row(inline_manual_keyboard_btn1, inline_manual_keyboard_btn2)

###############################     MANUAL KEYBOARD  #################################

inline_manual_video_keyboard = types.InlineKeyboardMarkup()
inline_manual_video_keyboard_btn1 = types.InlineKeyboardButton("5", callback_data="manual_video_5_keyboard")
inline_manual_video_keyboard_btn2 = types.InlineKeyboardButton("10", callback_data="manual_video_10_keyboard")
inline_manual_video_keyboard_btn3 = types.InlineKeyboardButton("15", callback_data="manual_video_15_keyboard")
inline_manual_video_keyboard_btn4 = types.InlineKeyboardButton("20", callback_data="manual_video_20_keyboard")
inline_manual_video_keyboard_btn5 = types.InlineKeyboardButton("25", callback_data="manual_video_25_keyboard")

inline_manual_video_keyboard.row(inline_manual_video_keyboard_btn1, inline_manual_video_keyboard_btn2,
                                 inline_manual_video_keyboard_btn3)

inline_manual_video_keyboard.row(inline_manual_video_keyboard_btn4, inline_manual_video_keyboard_btn5)

###############################     STREAMING KEYBOARD  #################################

inline_streaming_keyboard = types.InlineKeyboardMarkup()
inline_streaming_keyboard_btn1 = types.InlineKeyboardButton("\u2705 Activate", callback_data="activate_streaming_keyboard")
inline_streaming_keyboard_btn2 = types.InlineKeyboardButton("\u274C Deactivate", callback_data="deactivate_streaming_keyboard")

inline_streaming_keyboard.row(inline_streaming_keyboard_btn1, inline_streaming_keyboard_btn2)

###############################     CONFIGURATION PHOTO KEYBOARD  #################################

inline_photo_configuration_keyboard = types.InlineKeyboardMarkup()
inline_photo_configuration_keyboard_btn1 = types.InlineKeyboardButton("\U0001F533 Resolution",
                                                                      callback_data="resolution_configuration_photo_keyboard")
inline_photo_configuration_keyboard_btn2 = types.InlineKeyboardButton("\U0001F504 Rotation",
                                                                      callback_data="rotation_configuration_photo_keyboard")
inline_photo_configuration_keyboard_btn3 = types.InlineKeyboardButton("\u2B06 Vflip",
                                                                      callback_data="vflip_configuration_photo_keyboard")
inline_photo_configuration_keyboard_btn4 = types.InlineKeyboardButton("\u2B05 Hflip",
                                                                      callback_data="hflip_configuration_photo_keyboard")
inline_photo_configuration_keyboard_btn5 = types.InlineKeyboardButton("\u2B55 Show current configuration",
                                                                      callback_data="get_configuration_photo_keyboard")

inline_photo_configuration_keyboard.row(inline_photo_configuration_keyboard_btn1,
                                        inline_photo_configuration_keyboard_btn2)
inline_photo_configuration_keyboard.row(inline_photo_configuration_keyboard_btn3,
                                        inline_photo_configuration_keyboard_btn4)
inline_photo_configuration_keyboard.row(inline_photo_configuration_keyboard_btn5)

###############################    CONFIGURATION VIDEO KEYBOARD  #################################

inline_video_configuration_keyboard = types.InlineKeyboardMarkup()
inline_video_configuration_keyboard_btn1 = types.InlineKeyboardButton("\U0001F533 Resolution",
                                                                      callback_data="resolution_configuration_video_keyboard")
inline_video_configuration_keyboard_btn2 = types.InlineKeyboardButton("\U0001F504 Rotation",
                                                                      callback_data="rotation_configuration_video_keyboard")
inline_video_configuration_keyboard_btn3 = types.InlineKeyboardButton("\u2B06 Vflip",
                                                                      callback_data="vflip_configuration_video_keyboard")
inline_video_configuration_keyboard_btn4 = types.InlineKeyboardButton("\u2B05 Hflip",
                                                                      callback_data="hflip_configuration_video_keyboard")
inline_video_configuration_keyboard_btn5 = types.InlineKeyboardButton("\u23F3 Show datetime",
                                                                      callback_data="datetime_configuration_video_keyboard")
inline_video_configuration_keyboard_btn6 = types.InlineKeyboardButton("\u2B55 Show current configuration",
                                                                      callback_data="get_configuration_photo_keyboard")

inline_video_configuration_keyboard.row(inline_video_configuration_keyboard_btn1,
                                        inline_video_configuration_keyboard_btn2)
inline_video_configuration_keyboard.row(inline_video_configuration_keyboard_btn3,
                                        inline_video_configuration_keyboard_btn4,
                                        inline_video_configuration_keyboard_btn5)
inline_video_configuration_keyboard.row(inline_video_configuration_keyboard_btn6)

###############################    PHOTO RESOLUTION KEYBOARD  #################################

inline_photo_resolution_keyboard = types.InlineKeyboardMarkup()
inline_photo_resolution_keyboard_btn1 = types.InlineKeyboardButton("Low(640x480)",
                                                                   callback_data="low_photo_resolution_keyboard")
inline_photo_resolution_keyboard_btn2 = types.InlineKeyboardButton("Medium(1280x720)",
                                                                   callback_data="medium_photo_resolution_keyboard")
inline_photo_resolution_keyboard_btn3 = types.InlineKeyboardButton("High(1920x1080)",
                                                                   callback_data="high_photo_resolution_keyboard")
inline_photo_resolution_keyboard_btn4 = types.InlineKeyboardButton("Ultra(2592x1944)",
                                                                   callback_data="ultra_photo_resolution_keyboard")
inline_photo_resolution_keyboard_btn5 = types.InlineKeyboardButton("Show current resolution",
                                                                   callback_data="get_photo_resolution_keyboard")

inline_photo_resolution_keyboard.row(inline_photo_resolution_keyboard_btn1, inline_photo_resolution_keyboard_btn2)
inline_photo_resolution_keyboard.row(inline_photo_resolution_keyboard_btn3, inline_photo_resolution_keyboard_btn4)
inline_photo_resolution_keyboard.row(inline_photo_resolution_keyboard_btn5)

###############################    PHOTO ROTATION KEYBOARD  #################################

inline_photo_rotation_keyboard = types.InlineKeyboardMarkup()
inline_photo_rotation_keyboard_btn1 = types.InlineKeyboardButton("0", callback_data="photo_rotation_0_keyboard")
inline_photo_rotation_keyboard_btn2 = types.InlineKeyboardButton("90", callback_data="photo_rotation_90_keyboard")
inline_photo_rotation_keyboard_btn3 = types.InlineKeyboardButton("180",
                                                                 callback_data="photo_rotation_180_keyboard")
inline_photo_rotation_keyboard_btn4 = types.InlineKeyboardButton("270", callback_data="photo_rotation_270_keyboard")
inline_photo_rotation_keyboard_btn5 = types.InlineKeyboardButton("Show current rotation",
                                                                 callback_data="get_photo_rotation_keyboard")

inline_photo_rotation_keyboard.row(inline_photo_rotation_keyboard_btn1, inline_photo_rotation_keyboard_btn2,
                                   inline_photo_rotation_keyboard_btn3, inline_photo_rotation_keyboard_btn4)
inline_photo_rotation_keyboard.row(inline_photo_rotation_keyboard_btn5)

###############################    PHOTO VFLIP KEYBOARD  #################################

inline_photo_vflip_keyboard = types.InlineKeyboardMarkup()
inline_photo_vflip_keyboard_btn1 = types.InlineKeyboardButton("\u2705 Activate", callback_data="photo_activate_vflip_keyboard")
inline_photo_vflip_keyboard_btn2 = types.InlineKeyboardButton("\u274C Deactivate",
                                                              callback_data="photo_deactivate_vflip_keyboard")
inline_photo_vflip_keyboard_btn3 = types.InlineKeyboardButton("\u2B55 Show current value",
                                                              callback_data="get_photo_vflip_keyboard")
inline_photo_vflip_keyboard.row(inline_photo_vflip_keyboard_btn1, inline_photo_vflip_keyboard_btn2)
inline_photo_vflip_keyboard.row(inline_photo_vflip_keyboard_btn3)

###############################    PHOTO HFLIP KEYBOARD  #################################

inline_photo_hflip_keyboard = types.InlineKeyboardMarkup()
inline_photo_hflip_keyboard_btn1 = types.InlineKeyboardButton("\u2705 Activate", callback_data="photo_activate_hflip_keyboard")
inline_photo_hflip_keyboard_btn2 = types.InlineKeyboardButton("\u274C Deactivate",
                                                              callback_data="photo_deactivate_hflip_keyboard")
inline_photo_hflip_keyboard_btn3 = types.InlineKeyboardButton("\u2B55 Show current value",
                                                              callback_data="get_photo_hflip_keyboard")
inline_photo_hflip_keyboard.row(inline_photo_hflip_keyboard_btn1, inline_photo_hflip_keyboard_btn2)
inline_photo_hflip_keyboard.row(inline_photo_hflip_keyboard_btn3)

###############################    VIDEO RESOLUTION KEYBOARD  #################################

inline_video_resolution_keyboard = types.InlineKeyboardMarkup()
inline_video_resolution_keyboard_btn1 = types.InlineKeyboardButton("Low(640x480)",
                                                                   callback_data="low_video_resolution_keyboard")
inline_video_resolution_keyboard_btn2 = types.InlineKeyboardButton("Medium(1280x720)",
                                                                   callback_data="medium_video_resolution_keyboard")
inline_video_resolution_keyboard_btn3 = types.InlineKeyboardButton("High(1920x1080)",
                                                                   callback_data="high_video_resolution_keyboard")
inline_video_resolution_keyboard_btn4 = types.InlineKeyboardButton("Show current resolution",
                                                                   callback_data="get_video_resolution_keyboard")

inline_video_resolution_keyboard.row(inline_video_resolution_keyboard_btn1, inline_video_resolution_keyboard_btn2,
                                     inline_video_resolution_keyboard_btn3)
inline_video_resolution_keyboard.row(inline_video_resolution_keyboard_btn4)

###############################    VIDEO ROTATION KEYBOARD  #################################

inline_video_rotation_keyboard = types.InlineKeyboardMarkup()
inline_video_rotation_keyboard_btn1 = types.InlineKeyboardButton("0", callback_data="video_rotation_0_keyboard")
inline_video_rotation_keyboard_btn2 = types.InlineKeyboardButton("90", callback_data="video_rotation_90_keyboard")
inline_video_rotation_keyboard_btn3 = types.InlineKeyboardButton("180",
                                                                 callback_data="video_rotation_180_keyboard")
inline_video_rotation_keyboard_btn4 = types.InlineKeyboardButton("270", callback_data="video_rotation_270_keyboard")
inline_video_rotation_keyboard_btn5 = types.InlineKeyboardButton("Show current rotation",
                                                                 callback_data="get_video_rotation_keyboard")

inline_video_rotation_keyboard.row(inline_video_rotation_keyboard_btn1, inline_video_rotation_keyboard_btn2,
                                   inline_video_rotation_keyboard_btn3, inline_video_rotation_keyboard_btn4)
inline_video_rotation_keyboard.row(inline_video_rotation_keyboard_btn5)

###############################    VIDEO VFLIP KEYBOARD  #################################

inline_video_vflip_keyboard = types.InlineKeyboardMarkup()
inline_video_vflip_keyboard_btn1 = types.InlineKeyboardButton("\u2705 Activate", callback_data="video_activate_vflip_keyboard")
inline_video_vflip_keyboard_btn2 = types.InlineKeyboardButton("\u274C Deactivate",
                                                              callback_data="video_deactivate_vflip_keyboard")
inline_video_vflip_keyboard_btn3 = types.InlineKeyboardButton("\u2B55 Show current value",
                                                              callback_data="get_video_vflip_keyboard")
inline_video_vflip_keyboard.row(inline_video_vflip_keyboard_btn1, inline_video_vflip_keyboard_btn2)
inline_video_vflip_keyboard.row(inline_video_vflip_keyboard_btn3)

###############################    VIDEO HFLIP KEYBOARD  #################################

inline_video_hflip_keyboard = types.InlineKeyboardMarkup()
inline_video_hflip_keyboard_btn1 = types.InlineKeyboardButton("\u2705 Activate", callback_data="video_activate_hflip_keyboard")
inline_video_hflip_keyboard_btn2 = types.InlineKeyboardButton("\u274C Deactivate",
                                                              callback_data="video_deactivate_hflip_keyboard")
inline_video_hflip_keyboard_btn3 = types.InlineKeyboardButton("\u2B55 Show current value",
                                                              callback_data="get_video_hflip_keyboard")
inline_video_hflip_keyboard.row(inline_video_hflip_keyboard_btn1, inline_video_hflip_keyboard_btn2)
inline_video_hflip_keyboard.row(inline_video_hflip_keyboard_btn3)

###############################    VIDEO DATETIME KEYBOARD  #################################

inline_video_datetime_keyboard = types.InlineKeyboardMarkup()
inline_video_datetime_keyboard_btn1 = types.InlineKeyboardButton("\u2705 Activate",
                                                                 callback_data="video_activate_datetime_keyboard")
inline_video_datetime_keyboard_btn2 = types.InlineKeyboardButton("\u274C Deactivate",
                                                                 callback_data="video_deactivate_datetime_keyboard")
inline_video_datetime_keyboard_btn3 = types.InlineKeyboardButton("\u2B55 Show current value",
                                                                 callback_data="get_video_datetime_keyboard")
inline_video_datetime_keyboard.row(inline_video_datetime_keyboard_btn1, inline_video_datetime_keyboard_btn2)
inline_video_datetime_keyboard.row(inline_video_datetime_keyboard_btn3)


##############################################################################################
#                                                                                            #
#                             BOT INLINE KEYBOARD CALLBACK HANDLERS                          #
#                                                                                            #
##############################################################################################

###############################    DASHBOARD HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "mode_keyboard")
def mode_keyboard_callback(query):
    mode_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "configuration_keyboard")
def configuration_keyboard_callback(query):
    configuration_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "commands_keyboard")
def configuration_keyboard_callback(query):
    commands_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_mode_keyboard")
def get_mode_keyboard_callback(query):
    get_mode_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "toggle_detector_status_keyboard")
def toggle_detector_status_keyboard_callback(query):
    toggle_detector_status_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_detector_status_keyboard")
def get_detector_status_keyboard_callback(query):
    get_detector_status_keyboard(query)

##############################################################################################


###############################    MODE HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "manual_keyboard")
def manual_keyboard_callback(query):
    manual_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "automatic_keyboard")
def automatic_keyboard_callback(query):
    automatic_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "streaming_keyboard")
def streaming_keyboard_callback(query):
    streaming_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_mode_keyboard")
def get_mode_keyboard_callback(query):
    get_mode_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "toggle_detector_status_keyboard")
def toggle_detector_status_keyboard_callback(query):
    toggle_detector_status_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_detector_status_keyboard")
def get_detector_status_keyboard_callback(query):
    get_detector_status_keyboard(query)

##############################################################################################

###############################    AUTOMATIC HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "automatic_photo_keyboard")
def photo_automatic_keyboard_callback(query):
    automatic_photo_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "automatic_video_keyboard")
def video_automatic_keyboard_callback(query):
    automatic_video_keyboard(query)

##############################################################################################

##############################    MANUAL HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "manual_photo_keyboard")
def photo_manual_keyboard_callback(query):
    manual_photo_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "manual_video_keyboard")
def manual_automatic_keyboard_callback(query):
    manual_video_keyboard(query)

##############################################################################################

###############################    MANUAL VIDEO HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "manual_video_5_keyboard")
def video_manual_5_keyboard_callback(query):
    video_manual_5_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "manual_video_10_keyboard")
def video_manual_10_keyboard_callback(query):
    video_manual_10_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "manual_video_15_keyboard")
def video_manual_15_keyboard_callback(query):
    video_manual_15_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "manual_video_20_keyboard")
def video_manual_20_keyboard_callback(query):
    video_manual_20_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "manual_video_25_keyboard")
def video_manual_25_keyboard_callback(query):
    video_manual_25_keyboard(query)

##############################################################################################

###############################    CONFIGURATION HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "configuration_photo_keyboard")
def configuration_photo_keyboard_callback(query):
    configuration_photo_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "configuration_video_keyboard")
def configuration_video_keyboard_callback(query):
    configuration_video_keyboard(query)

##############################################################################################

###############################    CONFIGURATION PHOTO HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "resolution_configuration_photo_keyboard")
def resolution_configuration_photo_keyboard_callback(query):
    resolution_configuration_photo_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "rotation_configuration_photo_keyboard")
def rotation_configuration_photo_keyboard_callback(query):
    rotation_configuration_photo_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "vflip_configuration_photo_keyboard")
def vflip_configuration_photo_keyboard_callback(query):
    vflip_configuration_photo_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "hflip_configuration_photo_keyboard")
def hflip_configuration_photo_keyboard_callback(query):
    hflip_configuration_photo_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_configuration_photo_keyboard")
def get_configuration_photo_keyboard_callback(query):
    get_configuration_photo_keyboard(query)

##############################################################################################

###############################    CONFIGURATION PHOTO RESOLUTION HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "low_photo_resolution_keyboard")
def low_photo_resolution_keyboard_callback(query):
    low_photo_resolution_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "medium_photo_resolution_keyboard")
def medium_photo_resolution_keyboard_callback(query):
    medium_photo_resolution_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "high_photo_resolution_keyboard")
def high_photo_resolution_keyboard_callback(query):
    high_photo_resolution_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "ultra_photo_resolution_keyboard")
def ultra_photo_resolution_keyboard_callback(query):
    ultra_photo_resolution_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_photo_resolution_keyboard")
def get_photo_resolution_keyboard_callback(query):
    get_photo_resolution_keyboard(query)

##############################################################################################

###############################    CONFIGURATION PHOTO ROTATION HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "photo_rotation_0_keyboard")
def photo_rotation_0_keyboard_callback(query):
    photo_rotation_0_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "photo_rotation_90_keyboard")
def photo_rotation_90_keyboard_callback(query):
    photo_rotation_90_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "photo_rotation_180_keyboard")
def photo_rotation_180_keyboard_callback(query):
    photo_rotation_180_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "photo_rotation_270_keyboard")
def photo_rotation_270_keyboard_callback(query):
    photo_rotation_270_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_photo_rotation_keyboard")
def get_photo_rotation_keyboard_callback(query):
    get_photo_rotation_keyboard(query)

##############################################################################################

###############################    CONFIGURATION PHOTO VFLIP HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "photo_activate_vflip_keyboard")
def photo_activate_vflip_keyboard_callback(query):
    photo_activate_vflip_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "photo_deactivate_vflip_keyboard")
def photo_deactivate_vflip_keyboard_callback(query):
    photo_deactivate_vflip_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_photo_vflip_keyboard")
def get_photo_vflip_keyboard_callback(query):
    get_photo_vflip_keyboard(query)

##############################################################################################

###############################    CONFIGURATION PHOTO HFLIP HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "photo_activate_hflip_keyboard")
def photo_activate_hflip_keyboard_callback(query):
    photo_activate_hflip_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "photo_deactivate_hflip_keyboard")
def photo_deactivate_hflip_keyboard_callback(query):
    photo_deactivate_hflip_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_photo_hflip_keyboard")
def get_photo_hflip_keyboard_callback(query):
    get_photo_hflip_keyboard(query)

##############################################################################################

###############################    CONFIGURATION VIDEO HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "resolution_configuration_video_keyboard")
def resolution_configuration_video_keyboard_callback(query):
    resolution_configuration_video_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "rotation_configuration_video_keyboard")
def rotation_configuration_video_keyboard_callback(query):
    rotation_configuration_video_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "vflip_configuration_video_keyboard")
def vflip_configuration_video_keyboard_callback(query):
    vflip_configuration_video_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "hflip_configuration_video_keyboard")
def hflip_configuration_video_keyboard_callback(query):
    hflip_configuration_video_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "hflip_configuration_video_keyboard")
def hflip_configuration_video_keyboard_callback(query):
    hflip_configuration_video_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_configuration_video_keyboard")
def get_configuration_video_keyboard_callback(query):
    get_configuration_video_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "datetime_configuration_video_keyboard")
def datetime_configuration_video_keyboard_callback(query):
    datetime_configuration_video_keyboard(query)

##############################################################################################

###############################    CONFIGURATION VIDEO RESOLUTION HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "low_video_resolution_keyboard")
def low_video_resolution_keyboard_callback(query):
    low_video_resolution_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "medium_video_resolution_keyboard")
def medium_video_resolution_keyboard_callback(query):
    medium_video_resolution_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "high_video_resolution_keyboard")
def high_video_resolution_keyboard_callback(query):
    high_video_resolution_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_video_resolution_keyboard")
def get_video_resolution_keyboard_callback(query):
    get_video_resolution_keyboard(query)

##############################################################################################

###############################    CONFIGURATION VIDEO ROTATION HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "video_rotation_0_keyboard")
def video_rotation_0_keyboard_callback(query):
    video_rotation_0_keyboard(query)

##############################################################################################


@bot.callback_query_handler(lambda query: query.data == "video_rotation_90_keyboard")
def video_rotation_90_keyboard_callback(query):
    video_rotation_90_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "video_rotation_180_keyboard")
def video_rotation_180_keyboard_callback(query):
    video_rotation_180_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "video_rotation_270_keyboard")
def video_rotation_270_keyboard_callback(query):
    video_rotation_270_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_video_rotation_keyboard")
def get_video_rotation_keyboard_callback(query):
    get_video_rotation_keyboard(query)

##############################################################################################

###############################    CONFIGURATION VIDEO VFLIP HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "video_activate_vflip_keyboard")
def video_activate_vflip_keyboard_callback(query):
    video_activate_vflip_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "video_deactivate_vflip_keyboard")
def video_deactivate_vflip_keyboard_callback(query):
    video_deactivate_vflip_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_video_vflip_keyboard")
def get_video_vflip_keyboard_callback(query):
    get_video_vflip_keyboard(query)

##############################################################################################

###############################    CONFIGURATION VIDEO HFLIP HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "video_activate_hflip_keyboard")
def video_activate_hflip_keyboard_callback(query):
    video_activate_hflip_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "video_deactivate_hflip_keyboard")
def video_deactivate_hflip_keyboard_callback(query):
    video_deactivate_hflip_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_video_hflip_keyboard")
def get_video_hflip_keyboard_callback(query):
    get_video_hflip_keyboard(query)

##############################################################################################

###############################    CONFIGURATION VIDEO DATETIME HANDLERS   #################################

@bot.callback_query_handler(lambda query: query.data == "video_activate_datetime_keyboard")
def video_activate_datetime_keyboard_callback(query):
    video_activate_datetime_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "video_deactivate_datetime_keyboard")
def video_deactivate_datetime_keyboard_callback(query):
    video_deactivate_datetime_keyboard(query)

##############################################################################################

@bot.callback_query_handler(lambda query: query.data == "get_video_datetime_keyboard")
def get_video_datetime_keyboard_callback(query):
    get_video_datetime_keyboard(query)

##############################################################################################

##############################################################################################
#                                                                                            #
#                             BOT INLINE KEYBOARD RESPONSE FUNCTIONS                         #
#                                                                                            #
##############################################################################################

###############################      DASHBOARD FUNCTIONS   ###################################

def mode_keyboard(query):
    chat_id = query.message.chat.id
    bot.send_message(chat_id, "\u2B50 Mode selection: Choose one: ", reply_markup=inline_mode_keyboard)

##############################################################################################

def configuration_keyboard(query):
    chat_id = query.message.chat.id
    bot.send_message(chat_id, "\U0001F527 Configuration selection:", reply_markup=inline_configuration_keyboard)

##############################################################################################

def commands_keyboard(query):
    chat_id = query.message.chat.id

    command_message = '' + \
"""
** \U0001F4BB Available Commands \U0001F4BB **
-------------------- 
Below is a list of available commands to use. 
It is recommended that you use the interface, as there are more
extensive and intuitive features than by commands.

- Button interface:
----------------
/start: Access to the main application interface.

- Actions:
-----------
/photo: Take a photo and send it to the conversation.
/video <seconds>: Record a video with a duration <seconds> and send it to the conversation.
By default, the duration is 10 seconds.
/detector: Activates and deactivates the filtering of images in automatic mode in which people are detected.
/gmode: Returns current detector status (if detector is activated or deactivated).

- Modes:
------
/manual: Activates the manual mode.
/automatic <photo|video> Activates automatic mode in photo or video mode.
/streaming: Activates live video streaming.
/gmode: Shows current mode.

- Utility
-------
/id: Returns your telegram user id.
/username: Returns your telegram username.
/credentials: Returns your telegram user id and username.
"""

    bot.send_message(chat_id, command_message)

##############################################################################################

###############################      MODE FUNCTIONS   #################################

def manual_keyboard(query):
    message = query.message
    enable_manual_mode_bot(message)
    bot.send_message(message.chat.id, "\U0001F446 Choose an action: ", reply_markup=inline_manual_keyboard)

##############################################################################################

def automatic_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F2 Automatic mode: Select resource:", reply_markup=inline_automatic_keyboard)

##############################################################################################

def streaming_keyboard(query):
    message = query.message
    enable_streaming_mode_bot(message)

##############################################################################################

def get_mode_keyboard(query):
    message = query.message
    get_mode_bot(message)

##############################################################################################

def toggle_detector_status_keyboard(query):
    message = query.message
    toogle_detector_bot(message)

##############################################################################################

def get_detector_status_keyboard(query):
    message = query.message
    get_detector_status_bot(message)

##############################################################################################

###############################      AUTOMATIC FUNCTIONS   #################################

def automatic_photo_keyboard(query):
    message = query.message
    enable_automatic_mode_bot(message, motion_agent_mode="photo")

##############################################################################################

def automatic_video_keyboard(query):
    message = query.message
    enable_automatic_mode_bot(message, motion_agent_mode="video")

##############################################################################################

###############################      MANUAL VIDEO FUNCTIONS   #################################

def manual_photo_keyboard(query):
    message = query.message
    send_photo_bot(message)

##############################################################################################

def manual_video_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F9 Select seconds number", reply_markup=inline_manual_video_keyboard)

###############################      MANUAL VIDEO FUNCTIONS   #################################

def video_manual_5_keyboard(query):
    message = query.message
    send_video_bot(message, record_time=5)

##############################################################################################

def video_manual_10_keyboard(query):
    message = query.message
    send_video_bot(message, record_time=10)

##############################################################################################

def video_manual_15_keyboard(query):
    message = query.message
    send_video_bot(message, record_time=15)

##############################################################################################

def video_manual_20_keyboard(query):
    message = query.message
    send_video_bot(message, record_time=20)

##############################################################################################

def video_manual_25_keyboard(query):
    message = query.message
    send_video_bot(message, record_time=25)

##############################################################################################

###############################      CONFIGURATION FUNCTIONS   #################################

def configuration_photo_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F7\U0001F527 Photo configuration:", reply_markup=inline_photo_configuration_keyboard)

##############################################################################################

def configuration_video_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F9\U0001F527 Video configuration:", reply_markup=inline_video_configuration_keyboard)

##############################################################################################

###############################      CONFIGURATION PHOTO FUNCTIONS   #################################

def resolution_configuration_photo_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F7\U0001F533 Photo resolution configuration:", reply_markup=inline_photo_resolution_keyboard)

##############################################################################################

def rotation_configuration_photo_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F7\U0001F504 Photo rotation configuration:", reply_markup=inline_photo_rotation_keyboard)

##############################################################################################

def vflip_configuration_photo_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F7\U0001F504 Photo vflip configuration:", reply_markup=inline_photo_vflip_keyboard)

##############################################################################################

def hflip_configuration_photo_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F7\U0001F504 Photo hflip configuration:", reply_markup=inline_photo_hflip_keyboard)

##############################################################################################

def get_configuration_photo_keyboard(query):
    message = query.message

    try:
        photo_configuration_dictionary = get_module_configuration("photo")
        configuration_info = "The current photo configuration is: \n"
        for parameter, value in photo_configuration_dictionary.items():
            configuration_info += "- {}: {}\n".format(parameter, value)

        bot.send_message(message.chat.id, configuration_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the photo configuration")

##############################################################################################

###############################      CONFIGURATION PHOTO RESOLUTION FUNCTIONS   #################################

def low_photo_resolution_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="resolution", value="LOW")
        bot.send_message(message.chat.id, "Photo resolution updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo resolution")

##############################################################################################

def medium_photo_resolution_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="resolution", value="MEDIUM")
        bot.send_message(message.chat.id, "Photo resolution updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo resolution")

##############################################################################################

def high_photo_resolution_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="resolution", value="HIGH")
        bot.send_message(message.chat.id, "Photo resolution updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo resolution")

##############################################################################################

def ultra_photo_resolution_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="resolution", value="ULTRA")
        bot.send_message(message.chat.id, "Photo resolution updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo resolution")

##############################################################################################

def get_photo_resolution_keyboard(query):
    message = query.message

    try:
        resolution = get_module_parameter_configuration("photo", "resolution")

        if resolution == "LOW":
            resolution_info = "The current resolution is: LOW(640x480) \n".format()
        elif resolution == "MEDIUM":
            resolution_info = "The current resolution is: MEDIUM(1280x720) \n".format()
        elif resolution == "HIGH":
            resolution_info = "The current resolution is: HIGH(1920x1080) \n".format()
        elif resolution == "ULTRA":
            resolution_info = "The current resolution is: ULTRA(2592x1944) \n".format()
        else:
            resolution_info = "Sorry, could not read the photo resolution"

        bot.send_message(message.chat.id, resolution_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the photo resolution")

##############################################################################################

###############################      CONFIGURATION PHOTO ROTATION FUNCTIONS   #################################

def photo_rotation_0_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="rotation", value=0)
        bot.send_message(message.chat.id, "Updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo rotation")

##############################################################################################

def photo_rotation_90_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="rotation", value=90)
        bot.send_message(message.chat.id, "Updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo rotation")

##############################################################################################

def photo_rotation_180_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="rotation", value=180)
        bot.send_message(message.chat.id, "Rotation updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo rotation")

##############################################################################################

def photo_rotation_270_keyboard(query):
    message = query.message
    try:
        set_module_parameter_configuration(module="photo", parameter="rotation", value=270)
        bot.send_message(message.chat.id, "Rotation updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo rotation")

##############################################################################################

def get_photo_rotation_keyboard(query):
        message = query.message

        try:
            rotation = get_module_parameter_configuration("photo", "rotation")
            rotation_info = "The current rotation is: {}".format(rotation)

            bot.send_message(message.chat.id, rotation_info)
        except:
            bot.send_message(message.chat.id, "Sorry, could not read the photo rotation")

##############################################################################################

###############################      CONFIGURATION PHOTO VFLIP FUNCTIONS   #################################

def photo_activate_vflip_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="vflip", value=True)
        bot.send_message(message.chat.id, "Photo vflip activated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not activate photo vflip")

##############################################################################################

def photo_deactivate_vflip_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="vflip", value=False)
        bot.send_message(message.chat.id, "Photo vflip deactivated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not deactivate photo vflip")

##############################################################################################

def get_photo_vflip_keyboard(query):
    message = query.message

    try:
        rotation = get_module_parameter_configuration("photo", "vflip")
        rotation_info = "The current vflip value is: {}".format(rotation)

        bot.send_message(message.chat.id, rotation_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the photo vflip")

##############################################################################################

###############################      CONFIGURATION PHOTO HFLIP FUNCTIONS   #################################

def photo_activate_hflip_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="hflip", value=True)
        bot.send_message(message.chat.id, "Photo hflip activated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not activate photo hflip")

##############################################################################################

def photo_deactivate_hflip_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="photo", parameter="hflip", value=False)
        bot.send_message(message.chat.id, "Photo hflip deactivated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not deactivate photo hflip")

##############################################################################################

def get_photo_hflip_keyboard(query):
    message = query.message

    try:
        rotation = get_module_parameter_configuration("photo", "hflip")
        rotation_info = "The current hflip value is: {}".format(rotation)

        bot.send_message(message.chat.id, rotation_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the photo hflip")

##############################################################################################

###############################      CONFIGURATION VIDEO FUNCTIONS   #################################

def resolution_configuration_video_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F9\U0001F533 Video resolution configuration:", reply_markup=inline_video_resolution_keyboard)

##############################################################################################

def rotation_configuration_video_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F9\U0001F504 Video rotation configuration:", reply_markup=inline_video_rotation_keyboard)

##############################################################################################

def vflip_configuration_video_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F9\u2B06 Video vflip configuration:", reply_markup=inline_video_vflip_keyboard)

##############################################################################################

def hflip_configuration_video_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F9\u2B05 Video hflip configuration:", reply_markup=inline_video_hflip_keyboard)

##############################################################################################

def datetime_configuration_video_keyboard(query):
    message = query.message
    bot.send_message(message.chat.id, "\U0001F4F9\u23F3 Video datetime configuration:", reply_markup=inline_video_datetime_keyboard)

##############################################################################################

def get_configuration_video_keyboard(query):
    message = query.message

    try:
        video_configuration_dictionary = get_module_configuration("video")
        configuration_info = "The current video configuration is: \n"
        for parameter, value in video_configuration_dictionary.items():
            configuration_info += "- {}: {}\n".format(parameter, value)

        bot.send_message(message.chat.id, configuration_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the video configuration")

##############################################################################################

###############################      CONFIGURATION VIDEO RESOLUTION FUNCTIONS   #################################

def low_video_resolution_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="resolution", value="LOW")
        bot.send_message(message.chat.id, "Video resolution updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update video resolution")

##############################################################################################

def medium_video_resolution_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="resolution", value="MEDIUM")
        bot.send_message(message.chat.id, "Video resolution updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update video resolution")

##############################################################################################

def high_video_resolution_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="resolution", value="HIGH")
        bot.send_message(message.chat.id, "Video resolution updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update photo resolution")

##############################################################################################

def get_video_resolution_keyboard(query):
    message = query.message

    try:
        resolution = get_module_parameter_configuration("video", "resolution")

        if resolution == "LOW":
            resolution_info = "The current resolution is: LOW(640x480) \n".format()
        elif resolution == "MEDIUM":
            resolution_info = "The current resolution is: MEDIUM(1280x720) \n".format()
        elif resolution == "HIGH":
            resolution_info = "The current resolution is: HIGH(1920x1080) \n".format()
        else:
            resolution_info = "Sorry, could not read the video resolution"

        bot.send_message(message.chat.id, resolution_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the video resolution")

##############################################################################################

###############################      CONFIGURATION VIDEO ROTATION FUNCTIONS   #################################

def video_rotation_0_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="rotation", value=0)
        bot.send_message(message.chat.id, "Updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update video rotation")

##############################################################################################

def video_rotation_90_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="rotation", value=90)
        bot.send_message(message.chat.id, "Updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update video rotation")

##############################################################################################

def video_rotation_180_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="rotation", value=180)
        bot.send_message(message.chat.id, "Rotation updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update video rotation")

##############################################################################################

def video_rotation_270_keyboard(query):
    message = query.message
    try:
        set_module_parameter_configuration(module="video", parameter="rotation", value=270)
        bot.send_message(message.chat.id, "Rotation updated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not update video rotation")

##############################################################################################

def get_video_rotation_keyboard(query):
        message = query.message

        try:
            rotation = get_module_parameter_configuration("video", "rotation")
            rotation_info = "The current rotation is: {}".format(rotation)

            bot.send_message(message.chat.id, rotation_info)
        except:
            bot.send_message(message.chat.id, "Sorry, could not read the video rotation")

##############################################################################################

###############################      CONFIGURATION VIDEO VFLIP FUNCTIONS   #################################

def video_activate_vflip_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="vflip", value=True)
        bot.send_message(message.chat.id, "Video vflip activated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not activate video vflip")

##############################################################################################

def video_deactivate_vflip_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="vflip", value=False)
        bot.send_message(message.chat.id, "Video vflip deactivated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not deactivate video vflip")

##############################################################################################

def get_video_vflip_keyboard(query):
    message = query.message

    try:
        rotation = get_module_parameter_configuration("video", "vflip")
        rotation_info = "The current vflip value is: {}".format(rotation)

        bot.send_message(message.chat.id, rotation_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the video vflip")

##############################################################################################

###############################      CONFIGURATION VIDEO HFLIP FUNCTIONS   #################################

def video_activate_hflip_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="hflip", value=True)
        bot.send_message(message.chat.id, "Video hflip activated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not activate video hflip")

##############################################################################################

def video_deactivate_hflip_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="hflip", value=False)
        bot.send_message(message.chat.id, "Video hflip deactivated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not deactivate video hflip")

##############################################################################################

def get_video_hflip_keyboard(query):
    message = query.message

    try:
        rotation = get_module_parameter_configuration("video", "hflip")
        rotation_info = "The current hflip value is: {}".format(rotation)

        bot.send_message(message.chat.id, rotation_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the video hflip")

##############################################################################################

###############################      CONFIGURATION VIDEO DATETIME FUNCTIONS   #################################

def video_activate_datetime_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="showDatetime", value=True)
        bot.send_message(message.chat.id, "Video showDatetime activated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not activate video showDatetime")

##############################################################################################

def video_deactivate_datetime_keyboard(query):
    message = query.message

    try:
        set_module_parameter_configuration(module="video", parameter="showDatetime", value=False)
        bot.send_message(message.chat.id, "Video showDatetime deactivated successfully")
    except:
        bot.send_message(message.chat.id, "Sorry, Could not deactivate video showDatetime")

##############################################################################################

def get_video_datetime_keyboard(query):
    message = query.message

    try:
        rotation = get_module_parameter_configuration("video", "showDatetime")
        rotation_info = "The current showDatetime value is: {}".format(rotation)

        bot.send_message(message.chat.id, rotation_info)
    except:
        bot.send_message(message.chat.id, "Sorry, could not read the video showDatetime")


######################################  END INTERFACE  ######################################

logger = TelegramBotAgentLogger()

# bot running
bot.polling(none_stop=True)
