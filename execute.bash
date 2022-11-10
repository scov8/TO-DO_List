#!/bin/bash
# get current dir
PROJECT_DIR="$( cd "$( dirname "$0" )" && pwd )"
cd "$PROJECT_DIR/"
# move in chatbot_ws and build with catkin
PROJECT_DIR="$PROJECT_DIR/ros_chatbot/chatbot_ws"
cd "$PROJECT_DIR"
catkin clean --yes && catkin init
catkin build && source devel/setup.bash
catkin build

# run the launch file
roslaunch rasa_ros dialogue.xml
