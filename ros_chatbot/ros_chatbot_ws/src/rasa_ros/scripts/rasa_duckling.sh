#!/bin/bash

cd /media/psf/TO-DO_List/ros_chatbot/ros_chatbot_ws/src/rasa_ros/chatbot

PWD="Appl310!"
echo $PWD | sudo -S docker run -p 8000:8000 rasa/duckling 
