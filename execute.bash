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
gnome-terminal -- bash -c "source $PROJECT_DIR/devel/setup.bash; roscore; read"
gnome-terminal --tab -- bash -c "source $PROJECT_DIR/devel/setup.bash; roslaunch --wait pepper_nodes pepper_bringup.launch; read"
gnome-terminal -- bash -c "source $PROJECT_DIR/devel/setup.bash; roslaunch --wait pepper_nodes tts.launch; read"
gnome-terminal -- bash -c "source $PROJECT_DIR/devel/setup.bash; roslaunch --wait ros_audio_pkg speech_recognition.launch; read"
gnome-terminal -- bash -c "source $PROJECT_DIR/devel/setup.bash; roslaunch --wait face_recognition face_recognition.launch; read"
gnome-terminal -- bash -c "source $PROJECT_DIR/devel/setup.bash; roslaunch --wait rasa_ros dialogue.xml; read"
gnome-terminal -- bash -c "source $PROJECT_DIR/devel/setup.bash; rostopic echo /voice_txt; read"