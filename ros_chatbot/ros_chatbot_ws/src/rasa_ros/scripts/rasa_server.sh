#!/bin/bash

cd /media/psf/TO-DO_List/ros_chatbot/ros_chatbot_ws/src/rasa_ros/chatbot

rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials.yml --enable-api
