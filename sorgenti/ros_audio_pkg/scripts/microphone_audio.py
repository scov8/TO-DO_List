#!/usr/bin/env python3
import numpy as np
import pyaudio
import speech_recognition as sr
from config import *
import rospy
from std_msgs.msg import Int16MultiArray

# import the MicrophoneAudio service
from ros_audio_pkg.srv import MicrophoneAudio, MicrophoneAudioResponse

NAME = 'microphone_audio_server'

FORMAT = pyaudio.paInt16
CHANNELS = 0
WIN_SIZE_SEC = 0.03
CHUNK = int(WIN_SIZE_SEC * SAMPLE_RATE)
y  = Int16MultiArray()

def microphone_audio(req):
    def callback(recognizer, audio):
        data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
        data_to_send = Int16MultiArray()
        data_to_send.data = data
        y.data = data
        return MicrophoneAudioResponse(data_to_send)
        
    print("Calibrating...")
    with m as source:
        r.adjust_for_ambient_noise(source,duration=3)  
    print("Calibration finished")

    # start listening in the background
    # `stop_listening` is now a function that, when called, stops background listening
    print("Recording...")
    stop_listening = r.listen_in_background(m, callback)
    return MicrophoneAudioResponse(y)

def microphone_audio_server():
    rospy.init_node(NAME)
    s = rospy.Service('microphone_audio', MicrophoneAudio, microphone_audio)

    # spin() keeps Python from exiting until node is shutdown
    rospy.spin()


if __name__ == "__main__":
    r = sr.Recognizer()
    m = sr.Microphone(device_index=None,
                            sample_rate=SAMPLE_RATE,
                            chunk_size=CHUNK)
    microphone_audio_server()