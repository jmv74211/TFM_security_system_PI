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


def get_file_time(filename):
    # Remove extension file
    data_filtered = filename.replace('.jpg', '')
    data_filtered = data_filtered.replace('.mp4', '')

    # split by separator char
    data_filtered = data_filtered.split("_")

    hour = data_filtered[3][:2]
    minutes = data_filtered[3][2:4]
    seconds = data_filtered[3][4:6]

    time = "{}:{}:{}".format(hour, minutes, seconds)

    return time


##############################################################################################

"""
    Take a photo and send it using /photo command
"""


@bot.message_handler(commands=['photo'])
@authtentication_required
def send_photo(message):
    chat_id = message.chat.id

    payload = {'user': api_agent_user, 'password': api_agent_password}

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

    task_finished = False

    photo_path = ''

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

    logger.info("Photo taken at {} is being sending...".format(get_file_time(photo_path)))

    bot.send_message(chat_id, "Photo taken at {} is being sending...".format(get_file_time(photo_path)))

    photo = open(photo_path, 'rb')

    bot.send_photo(chat_id, photo)

    photo.close()

    logger.debug("Photo has been sent")

############################################################################################


logger = TelegramBotAgentLogger()

# bot running
bot.polling(none_stop=True)
