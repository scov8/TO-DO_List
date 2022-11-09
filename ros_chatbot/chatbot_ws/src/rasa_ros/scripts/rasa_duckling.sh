#!/bin/bash

PWD="Appl310!"
echo $PWD | sudo -S docker run -p 8000:8000 rasa/duckling 