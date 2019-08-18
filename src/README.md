# SRC App

The application is responsible for interacting with the hardware through a set of microservices and modules connected to a main API. 
It is composed of the [following elements](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src):

 - [agents](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/agents): Agents are the main 
processes that interact with the modules and communicate directly with the API. They are the following:
  - [api_agent.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/agents/api_agent.py): It 
  is the main agent, which manages the restful API to interact with the set of system elements.
  
 - [motion_agent.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/agents/motion_agent.py): 
  The motion agent is a process in charge of detecting movement through the motion sensor, and consequently make a photo or video recording, and:
  
     + If the object **detector mode is activated**, it will send a request to the [object detector agent](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/agents/object_detector_agent.py)
     , to detect if there is any person in the photo. In this case, it will generate an alert to the api agent, otherwise it will not  be sent.
     
     + If the **object detector mode is disabled**, an alert will be sent to the api agent directly.
   
 - [object_detector_agent.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/agents/object_detector_agent.py): 
   It is a small restful api that receives requests with an image path and responds with a list of objects detected in that image. 
   To do this, it makes use of the [object detector module](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/modules/object_detector)
   that has been programmed using the `tensorflow` framework.
   
 - [config](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/config): Directory where the 
 default configuration modules and the authentication file for the login module are stored. It contains:
   - [authentication.yml](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/config/authentication.yml): 
   File where is saved the user and password authentication info. The password is encrypted with the SHA256 algorithm, 
   obtained through the [generate hash password tool](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/tools/generate_hash_password.py).
   
   - [modules_config.yml](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/config/modules_config.yml): Default modules config, that can be modified in the 
   frontend app by the user.
   
 - [lib](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/lib): Directory where auxiliary functions have been stored:
   - [flask_celery.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/lib/flask_celery.py): 
   Function to build and configure the flask celery instance.
 
 - [modules](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/modules): Directory that contains the 
 modules of the backend application. It is composed by the following elements:
   - [object_detector](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/modules/object_detector):
   Directory where all the source code, models and libraries of tensorflow have been stored to make the object detector agent work.
   
   - [pistream](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/modules/pistream): Directory 
   where the [streaming server](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/modules/pistream/streaming_server.py) 
   module has been stored.
   
   - [authentication.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/modules/authentication.py): 
   Authentication module to authenticate requests to the api agent.
   
   - [logger.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/modules/logger.py): 
   Logging module to store logs of each module and agent in different log files.
   
   - [photo.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/modules/photo.py): Module 
   for configuring and taking photos with the official raspberry camera: `Raspicam`.
   
   - [video.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/modules/video.py): Module 
   for configuring and recording videos with the official raspberry camera: `Raspicam`.
   
 - [tools](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/tools): Directory that 
 contains some support modules. It contains: 
   - [generate_hash_password.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/tools/generate_hash_password.py):
   Script to insert a password and return the hash generated using the SHA256 algorithm. This script is usually used 
   to add the encrypted password into the [authentication.yml](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/config/authentication.yml) file. 
 
 - [settings.py](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/tools): Backend application configuration file.


