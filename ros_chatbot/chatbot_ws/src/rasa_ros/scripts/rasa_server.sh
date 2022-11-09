#!/bin/bash

BOT_DIR="/media/psf/TO-DO_List/ros_chatbot/chatbot_ws/src/rasa_ros/chatbot"

cd $BOT_DIR

rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials.yml --enable-api
