#!/bin/bash
#install ros
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt install curl 
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -

sudo apt update
sudo apt install ros-noetic-desktop-full
source /opt/ros/noetic/setup.bash
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc source ~/.bashrc

sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential sudo apt install python3-rosdep
sudo rosdep init
rosdep update

sudo apt-get install python3-catkin-tools

# to install cmake
sudo apt-get install build-essential libssl-dev
cd /tmp
wget https://github.com/Kitware/CMake/releases/download/v3.20.0/cmake-3.20.0.tar.gz
tar -zxvf cmake-3.20.0.tar.gz
cd cmake-3.20.0
./bootstrap
make
sudo make install
cmake --version

#install RASA
sudo apt update
sudo apt install python3-pip
python3 -m pip install pip==22.0.0
python3 -m pip install -U pyOpenSSL
python3 -m pip install rasa==2.7.2
python3 -m pip install rasa[spacy]
python3 -m pip install rasa[transformers]