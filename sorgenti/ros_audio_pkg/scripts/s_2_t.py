#!/usr/bin/env python3
import rospy
from std_msgs.msg import Int16MultiArray, String
import numpy as np
from speech_recognition import AudioData
import speech_recognition as sr
import sys
import os
from ros_audio_pkg.srv import *
import time


def s_2_t():
    r = sr.Recognizer()
    rospy.wait_for_service('microphone_audio') #aspetto che mi connetto dal server, il nome è lo stesso che ho messo al server
    
    try:
        # create a handle to the add_two_ints service
        xxx = rospy.ServiceProxy('microphone_audio', MicrophoneAudio)
        
        # simplified style
        #resp1 = xxx()

        # formal style
        resp1 = xxx.call(MicrophoneAudioRequest())

        data = np.array(resp1.output,dtype=np.object) #int16
        audio_data = AudioData(data.tobytes(), 16000, 2)

        try:
            spoken_text= r.recognize_google(audio_data, language='it-IT')
            print("Google Speech Recognition pensa tu abbia detto: " + spoken_text)
        except sr.UnknownValueError:
            print("Google Speech Recognition non riesce a capire da questo file audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)
    

if __name__ == '__main__':
    s_2_t()
    
