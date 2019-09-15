# User guide

The application is very easy to use. It basically consists of a telegram bot that controls a restful API.
Through this telegram bot, we will be able to manage the set of modules of the application to take pictures, record videos,
activate the streaming...

You can activate the button interface by inserting the command /start or by typing any character

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_1.png">
</p>

As you can see, there is an interface of buttons through which we can select the different options.

- **Mode:** In this section we can select the mode of the application. We can activate the camera/video manually, activate
the motion sensor, streaming or the alerts filter using the detector.

- **Configuration:** In this section we can modify the configuration of the camera/video, modifying the resolution,
rotation, hflip or vflip.

- **Utils:** In this section we can visualize the credentials of the user of telegram and bot. This information can
be useful, as it is necessary to configure the telegram application and for the application to run correctly.

- **Commands:** This button shows all the commands available to interact with the application instead of using the
button interface.

- **Documentation:** This button will redirect you to the application documentation that is available in this repository.

## Mode

In this section you will find the following options:

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_2.png">
</p>

- **Manual:** Activates manual mode. You will be able to capture a photo or record a video specifying the number of
seconds of recording. After this capture or recording is finished, it will be sent to the conversation.

    > Taking a picture:

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_3.png">
    </p>

     > Recording a video:

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_4.png">
    </p>

- **Automatic:** Activates the automatic mode. In this mode the motion sensor will be activated and alerts will be sent
when some type of movement is detected, and its corresponding photo or video (according to the choice) to be able to
observe what is happening.

    > Activating automatic mode with photo alerts

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_5.png">
    </p>

- **Streaming:** Activates the streaming mode. In this mode, we will be able to observe in real time what the camera is visualizing. This retransmission is done in a responsive way, so it can be viewed through the browser of any device.

    *Attention, the broadcast will not be stored, but will only be retransmitted.*

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_6.png">
    </p>

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_7.png">
    </p>

- **Get current status:** The bot will tell you the current active mode

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_8.png">
    </p>

- **Toogle detector status:** Activates or deactivates the object detector mode.

    The functionality of this agent is to filter the captured images as alerts, and only send the alerts in which a person
    has been detected in the captured photo. The images catalogued as "false positives" will be sent to the directory
    specified in the [settings.py](https://github.com/jmv74211/TFM_security_system_PI/blob/master/src/settings.py) file.

    > **Note**: It is important to know that it only has to be activated in the case of a full installation and the object
    detector agent process is running.It is recommended to configure a medium resolution (1280x720) for the camera,
    since on the contrary, the agent will take too long to process the image and the alerts will take too long to be
    sent to the conversation.

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_9.png">
    </p>

- **Get detector status:** The bot will tell you the current object detector mode status.

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_10.png">
    </p>

> **Note:** When a mode is activated, the previous mode is automatically deactivated, i.e., to deactivate a mode,
simply activate another mode.


## Configuration

In this section you can modify the camera and video settings.

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_11.png">
</p>

**Photo configuration**

Here you can change all the settings of the captured photos both in manual mode and in automatic mode with photos.

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_12.png">
</p>

- **Resolution:** Modify the resolution of the camera

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_13.png">
    </p>

- **Rotation:** Modify the rotation of the camera

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_14.png">
    </p>

- **Vflip:** Activate/deactivate the vertical flip of the camera

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_15.png">
    </p>

- **Hflip:** Activate/deactivate the horizontal flipof the camera

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_16.png">
    </p>

- **Show current configuration:** Send a message to the conversation with the current photo configuration.

    <p align="center">
      <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_17.png">
    </p>

**Video configuration**

Here you can change all the settings of the video recording, both in manual and automatic mode with video.

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_18.png">
</p>

In the video configuration, there are the same options as in the camera, adding show datetime, whose objective is to
show the date and time of the recording at the top of the video.

- Show datetime deactivated

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_19.png">
</p>

- Show datetime activated

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_20.png">
</p>

## Utils

In this section we can visualize the credentials of the user of telegram and bot. This information can
be useful, as it is necessary to configure the telegram application and for the application to run correctly.

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_21.png">
</p>

- User credentials

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_22.png">
</p>


- Bot credentials

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_23.png">
</p>

## Commands

You can also interact with the bot as a command (instead of the button interface). This option shows you the possible
commands with which you can interact with the bot, and may be able to speed up some task in certain cases.

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/user_guide_24.png">
</p>

## Documentation

This button redirects you to the application documentation page.
