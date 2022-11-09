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
chmod a+r /etc/apt/keyrings/docker.gpg
apt update
apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

