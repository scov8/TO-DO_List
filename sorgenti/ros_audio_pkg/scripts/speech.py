#!/usr/bin/env python3

import numpy as np
import pyaudio
import speech_recognition as sr
from config import *
import rospy
from std_msgs.msg import Int16MultiArray

SERVICE_NAME = 'microphoneAudio'
from ros_audio_pkg.srv import MicrophoneAudio, MicrophoneAudioResponse

FORMAT = pyaudio.paInt16
CHANNELS = 0
WIN_SIZE_SEC = 0.03
CHUNK = int(WIN_SIZE_SEC * SAMPLE_RATE)

class Speech():

    def __init__(self) -> None:
        self._r = sr.Recognizer()
        # Audio source
        self._m = sr.Microphone(device_index=None,
                            sample_rate=SAMPLE_RATE,
                            chunk_size=CHUNK)


    def start(self):
        """Start the node and calibrate the microphone to the local noise.
        """
        rospy.init_node('microphoneAudioNodeServer', anonymous=True)
        rospy.Service(SERVICE_NAME, MicrophoneAudio, self._microphone, buff_size=1)
        rospy.spin()
        

    def _microphone(self, req):
        # this is called from the background thread
        def _handle_sentence(audio):
            """ 
            la funzione listen_in_background ascolta tutto l'audio in background 
            e quando riconosce una frase questa fun viene attivata 
            """
            data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
            data_to_send = Int16MultiArray()
            data_to_send.data = data

            print(data)
            return MicrophoneAudioResponse(data_to_send)

        
        # Calibration within the environment
        # we only need to calibrate once, before we start listening
        print("Calibrating...")
        with self._m as source:
            self._r.adjust_for_ambient_noise(source, duration=3)
        print("Calibration finished")

        # start listening in the background
        # `stop_listening` is now a function that, when called, stops background listening
        print("Recording...")
        stop_listening = self._r.listen_in_background(self._m, _handle_sentence)
        
        stop_listening()
        

if __name__ == '__main__':
    node = Speech()
    node.start()