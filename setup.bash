#!/bin/bash
# installation of SQLite v.3
apt update && apt install sqlite3
sqlite3 --version

# unistall old version of docker
apt remove docker docker-engine docker.io containerd runc
# installation of docker
apt update
apt install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
chmod a+r /etc/apt/keyrings/docker.gpg
apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

python3 -m spacy download en_core_web_md

#install apache server and php for run the website
sudo apt install apache2 -y
sudo apt install php libapache2-mod-php php-mysql -y
apt install php7.4-sqlite3
apt install php-sqlite3

#Adding permissions to be able to run nodes 
chmod u+x ./ros_chatbot/chatbot_ws/src/rasa_ros/scripts/rasa_webserver.sh
chmod u+x ./ros_chatbot/chatbot_ws/src/rasa_ros/launch/*
chmod u+x ./ros_chatbot/chatbot_ws/src/rasa_ros/scripts/*
chmod u+x ./ros_chatbot/chatbot_ws/src/face_recognition/src/launch/face_recognition.launch
chmod u+x ./ros_chatbot/chatbot_ws/src/face_recognition/src/*
chmod u+x ./ros_chatbot/chatbot_ws/src/pepper_nodes/launch/pepper_bringup.launch
chmod u+x ./ros_chatbot/chatbot_ws/src/pepper_nodes/launch/tts.launch
chmod u+x ./ros_chatbot/chatbot_ws/src/pepper_nodes/src/*
chmod u+x ./ros_chatbot/chatbot_ws/src/ros_audio_pkg/launch/speech_recognition.launch
chmod u+x ./ros_chatbot/chatbot_ws/src/ros_audio_pkg/src/*
chmod u+x ./ros_chatbot/chatbot_ws/src/vision_msgs/*

#Create a symbolic link inside the apache root of the web site
chmod -R 777 /var/www/html/
ln -s ./ros_chatbot/chatbot_ws/src/rasa_ros/sito/ /var/www/html/