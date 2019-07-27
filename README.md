# TFM_security_system_PI
Security system for control and video surveillance implemented on a raspberry PI 

![Status](https://img.shields.io/badge/Status-documenting-orange.svg)
![Status](https://img.shields.io/badge/Status-developing-orange.svg)


<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/raspytel.png">
</p>

![Status](https://img.shields.io/badge/-RasperryPI-red.svg)
![Status](https://img.shields.io/badge/-Python-yellow.svg)
![Status](https://img.shields.io/badge/-Telegram-blue.svg)


# 1. Introduction

Security system PI is an application that allows us to build a security system based on low-cost video surveillance using a raspberry PI, a camera and a motion sensor.

The idea is to be able to control this device through a telegram bot connected to our API that controls the main system. The main functions are the following:
- Automatic system of alerts generated when capturing movement.
- Manual system to capture video or a photo instantly.
- Streaming system to visualize the image in real time.

---

# 2. Getting started.

## 2.1 Hardware required

As hardware devices to create our security system, we need the following components:

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/hardware_required.png">
</p>

When we talk about raspberry PI, we mean the set of elements necessary for it to work (Normally, it's always included in a pack), such as they are the powers upply unit and SD card where we have installed an SO (in this case Raspbian 9).

### 2.1.1 Hardware installation Guide

- First, you need to connect the raspicam to the raspberry PI and configure it to detect the camera. If you don't know how to do it, you can watch the following tutorial: https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera

- Once you have installed the camera and tested that it works, the next step is to install the motion sensor. To do this we have to connect the jumper wires as indicated in the following figure (pay attention to the colors that indicate where each pin has been connected)

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/hardware_connections.png">
</p>

- And that's it. Put the camera and sensor where you want to watch. For example, I have placed it as follows:

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/doc/images/raspberry_place.png">
</p>