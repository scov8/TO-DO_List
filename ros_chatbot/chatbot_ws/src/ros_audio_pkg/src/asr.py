#!/usr/bin/python3
import rospy
from std_msgs.msg import Int16MultiArray, String, Bool
import numpy as np

from speech_recognition import AudioData
import speech_recognition as sr

# Initialize a Recognizer
r = sr.Recognizer()

# Init node
rospy.init_node('speech_recognition', anonymous=True)
pub1 = rospy.Publisher('voice_data', Int16MultiArray, queue_size=10)
pub2 = rospy.Publisher('voice_txt', String, queue_size=10)

sub_syn_speech = rospy.Subscriber('parlando', Bool, queue_size=10)

tmp = Bool()
tmp.data = False

# this is called from the background thread
def callback(audio):
    global tmp
    data = np.array(audio.data,dtype=np.int16)
    audio_data = AudioData(data.tobytes(), 16000, 2)

    try:
        print(tmp)
        #spoken_text= r.recognize_google(audio_data, language='en-GB') # en-GB
        #print("Google Speech Recognition pensa tu abbia detto: " + spoken_text)
        '''
        #l'abbiamo messa sotto 
        try:
            tmp = rospy.wait_for_message("parlando", Bool, timeout=1)
        except:
           pass
        '''
        print("tmp   "+str(tmp.data))
        if not tmp.data:
            spoken_text= r.recognize_google(audio_data, language='en-GB') # en-GB
            print("Ecco cosa ha capito google, mo lo pubblico: " + spoken_text)
            pub1.publish(audio) # Publish audio only if it contains words
            pub2.publish(spoken_text)
        else:
            spoken_text= r.recognize_google(audio_data, language='en-GB') # en-GB
            print("Pepper sta parlando, ignoro il messaggio: " + spoken_text)
    except sr.UnknownValueError:
        print("Google Speech Recognition non riesce a capire da questo file audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

def listener():
    global tmp
    rospy.Subscriber("mic_data", Int16MultiArray, callback)
    #provare sta cosa qua dentro e vedere se funziona
    try:
        tmp = rospy.wait_for_message("parlando", Bool, timeout=1)
    except:
        pass

    rospy.spin()

if __name__ == '__main__':
    listener()
