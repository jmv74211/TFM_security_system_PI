from flask import Flask, request, jsonify      # Import to use web service
import yaml                                    # Import to read the configuration file information
import settings                                # Import setting info
from modules.photo import Photo                # Import Photo module

##############################################################################################

"""
    MAIN AGENT: Receives requests and interacts with the rest of system elements .
"""

# Main instance app
app = Flask(__name__)

##############################################################################################

@app.route("/api/take_photo",methods=['POST'])
def take_photo():

    photo_config = read_photo_configuration()

    camera_photo = Photo(file_path=settings.PHOTO_FILES_PATH, resolution=photo_config['resolution'],
                         vflip=photo_config['vflip'], hflip=photo_config['hflip'])
    camera_photo.rotate(photo_config['rotation'])
    camera_photo.take_photo()
    camera_photo.close()

    data = {"response" : "OK"}

    return jsonify(data)

##############################################################################################

def read_photo_configuration():
    with open(settings.CONFIG_FILE_MODULE_PATH, 'r') as ymlfile:
        module_settings = yaml.load(ymlfile, Loader=yaml.FullLoader)

    data = dict()

    data['resolution'] = module_settings['photo']['resolution']
    data['rotation'] = module_settings['photo']['rotation']
    data['vflip'] = module_settings['photo']['vflip']
    data['hflip'] = module_settings['photo']['hflip']

    return data


##############################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.API_AGENT_RUNNING_PORT, debug=settings.DEBUG)