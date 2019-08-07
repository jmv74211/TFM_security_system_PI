import yaml
from werkzeug.security import check_password_hash
import settings

with open(settings.CONFIG_FILE_AUTHENTICATION, 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

"""
    Security password has to be encrypted with generate_hash_password script that is
    in tools folder, and add the password hash to authentication password config file.

"""

security_user = cfg['authentication']['user']
password_security_user = cfg['authentication']['password']

##############################################################################################

def authenticate_user(username, password):
    check_password = check_password_hash(password_security_user, password)

    if (check_password and security_user == username):
        return True
    else:
        return False

##############################################################################################