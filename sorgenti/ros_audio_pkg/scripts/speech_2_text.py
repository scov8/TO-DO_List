#!/usr/bin/python3
import rospy
from std_msgs.msg import Int16MultiArray, String
import numpy as np

from speech_recognition import AudioData
import speech_recognition as sr

SERVICE_NAME = 'microphoneAudio'
from ros_audio_pkg.srv import MicrophoneAudio, MicrophoneAudioRequest, MicrophoneAudioResponse

class Speech2Text():
    def __init__(self) -> None:
        self._r = sr.Recognizer()

    def listen(self, *args):
        rospy.wait_for_service(SERVICE_NAME)
    
        microphone_audio = rospy.ServiceProxy(SERVICE_NAME, MicrophoneAudio) #, persistent=True)
        audio = microphone_audio.call(MicrophoneAudioRequest(*args))

        data = np.array(audio.output.data, dtype=np.int16)
        audio_data = AudioData(data.tobytes(), 16000, 2)
        try:
            spoken_text= self._r.recognize_google(audio_data)
            print("Google Speech Recognition pensa tu abbia detto: " + spoken_text)
            # check if there was a phrase in the audio
        except sr.UnknownValueError:
            print("Google Speech Recognition non riesce a capire da questo file audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return MicrophoneAudioResponse(String(spoken_text))
        
        

if __name__ == '__main__':
    s = Speech2Text()
    s.listen()
