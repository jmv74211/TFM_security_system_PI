# App deployment


In this section, we are going to see how we can configure and deploy the application.

> Note: Before starting to deploy the application, you must have done the installation. If you haven't done it yet, 
you can see the installation process in this **[link](https://github.com/jmv74211/TFM_security_system_PI/tree/master/doc/installation)**.

The steps to follow are:

- Create a telegram bot.
- Download the repository.
- Configure the app.
- Run the application.

## Create a telegram bot

Telegram is a cloud-based instant messaging and voice over IP service. Telegram  client apps are available for multiple platforms.

- First of all, you need to [download the application](https://telegram.org/), install it and register using your mobile number.

- Then, you must search for BotFather's name in the search engine.

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/config_1.png">
</p>

- Finally, you must start a conversation with this bot in order to create your own bot. To do this, you can use the 
command `/newbot` and the creation process will begin. It's very simple and quick, here's an example.

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/config_2.png">
</p>

> **Note**: Once the bot is created, it is very important that you save the API token, since it is necessary to insert it in 
the configuration that will be done in a few steps later.

---

## Download the repository

The repository contains all the source code you will need to build and run the application.

You can easily download and unzip it using the `git` tool using:

```bash
git clone https://github.com/jmv74211/TFM_security_system_PI.git | tar -xzvf
```

> **Note**: If you don't have the `git` tool installed, you can access the 
[repository page](https://github.com/jmv74211/TFM_security_system_PI) and download it with a zip file.

---

## Configure the app

To configure the app, you have to go to the 
[config](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/config) directory inside the 
[src](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src) folder and make the following settings:

 To do this, we will 
use the utility [generate_has_password.py]() that is inside the tools directory.

- First, let's **generate a password hash** for the API. To do this, we will use the utility 
[generate_has_password.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/tools/generate_hash_password.py) that is inside the 
[tools](https://github.com/jmv74211/TFM_security_system_PI/tree/master/src/tools) directory.

    To get the password hash, we have to:
    
    ```bash
    $ python3 generate_hash_password.py 
    Enter your password: password_test
    Your hash password is  sha256$hqhX2BpC$638ce4d67d539de73fd19e8e29e789b43b64a0d75b8f8d64266c303b3bf5826d
    ```
   
- Next, we need to enter the **login credentials** for our API. Go to the 
[authentication.yml](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/config/authentication.yml) 
file, and set the access credentials for the application API (You have to add your user and password hash that 
has been obtained in the previous step).

- The next step is to configure the **telegram credentials**. To do this, you have to edit the 
[telegram_config.yml](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/config/telegram_config.yml) file,
 and add the information that is requested in the template.

    > **Note**: If you don't know all the data, don't worry, they can be obtained later. The mandatory data are `api_token`, 
    `api_agent_user` and `api_agent_password`. (Note that in this case it is necessary to enter the password in raw format,
     (unencrypted)).

- If you have done a **full installation** (installed the necessary components for the object detector agent) then you have to set the value 
 of the `OBJECT_DETECTOR_INSTALLED` variable to *"true"* in app.sh to be able to start the object detection agent when running the application.

 - The last step of the configuration process is to modify the 
 [settings file](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/settings.py). 
 In this file, we can modify the general configuration of the application, such as IP addresses of services, ports...
    
   You can edit the information you need, but the minimum necessary is the following:
   
   - `API_AGENT_IP_ADDRESS`: IP address of the raspberry that is running the API service. If the installation is local, 
   enter the local IP address. *Example: 192.168.1.100*
   - `API_PASSWORD`: Your API agent raw password (unencrypted). *Example: "test"*
   - `GPIO_SENSOR_PIN_NUMBER`: Your GPIO sensor pin number where the motion sensor has been connected. If you have 
   followed the hardware installation above, then it will be number 16. Note that the numbering mode is `GPIO.BOARD`.
   - `STREAMING_SERVER_IP_ADDRESS`: IP address of the raspberry that is running the streaming service. If the installation is local, 
   enter the local IP address. *Example: 192.168.1.100*
   - `DETECTOR_AGENT_IP_ADDRESS`: IP address of the raspberry that is running the object detector service. If the installation is local, 
   enter the local IP address. *Example: 192.168.1.100*
   
> **Warning**: Be careful with the syntax and the information you are going to modify. Any error in the configuration files
 will make the application not work properly.

---
 
## Run the application.

Once the application is installed and configured, we can execute it using the
 [app.sh](https://github.com/jmv74211/TFM_security_system_PI/blob/master/app.sh) script located in the root 
directory of the application.

> **Note:** Remember that if you have done a complete installation (necessary components for the object detector agent) you have 
to set the value of the `OBJECT_DETECTOR_INSTALLED` variable to "true" in [app.sh](https://github.com/jmv74211/TFM_security_system_PI/blob/master/app.sh)
to be able to start all the services.

```bash
$ sudo chmod u+x ./app.sh
```

- To **start** the application, run the command:

    ```bash
    $ ./app.sh start
    ```

- To **stop** the application, run the command:

    ```bash
    $ ./app.sh stop
    ```
    
- To **check** the state of the application, run the command:

    ```bash
    $ ./app.sh status
    ```

> **Attention:** If you have not configured the telegram credentials (telegram username, id, bot username and bot id) you 
will only be able to access the utils section of the bot to obtain these credentials. Once obtained, add them to the 
configuration file, and restart the application (stop and start).