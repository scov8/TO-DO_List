#!/usr/bin/env python3
#   If you develop a new program, and you want it to be of the greatest
# possible use to the public, the best way to achieve this is to make it
# free software which everyone can redistribute and change under these terms.

#   To do so, attach the following notices to the program.  It is safest
# to attach them to the start of each source file to most effectively
# state the exclusion of warranty; and each file should have at least
# the "copyright" line and a pointer to where the full notice is found.

#        TO-DO List chat bot.
#        Copyright (C) 2022 - All Rights Reserved
#        Group:
#            Faiella Ciro              0622701816  c.faiella8@studenti.unisa.it
#            Giannino Pio Roberto      0622701713	p.giannino@studenti.unisa.it
#            Scovotto Luigi            0622701702  l.scovotto1@studenti.unisa.it
#            Tortora Francesco         0622701700  f.tortora21@studenti.unisa.it

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
import rospy
from std_msgs.msg import Int16MultiArray, String
import numpy as np

from speech_recognition import AudioData
import speech_recognition as sr

# Initialize a Recognizer
r = sr.Recognizer()

# Init node
rospy.init_node('speech_recognition', anonymous=True)
pub2 = rospy.Publisher('voice_txt', String, queue_size=10)
pub3 = rospy.Publisher('bot_answer', String, queue_size=10)

# this is called from the background thread
def callback(audio):
    """
    This callback takes as input the audio track and sends it to google recognizer to
    extract the sentence.
    """
    data = np.array(audio.data, dtype=np.int16)
    audio_data = AudioData(data.tobytes(), 16000, 2)
    try:
        spoken_text = r.recognize_google(audio_data, language='en-GB') # en-GB
        print("Here's what google understood, I'm posting it: " + spoken_text)
        pub2.publish(spoken_text)
    except sr.UnknownValueError:
        pub3.publish("")
        print("Google Speech Recognition cannot understand from this audio file")
    except sr.RequestError as e:
        pub3.publish("I'm offline")
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

def listener():
    """
    This function when 'mic_data' topic publish something, the callback is activated passing as input the
    Int16MultiArray which represent the audio track
    """
    rospy.Subscriber("mic_data", Int16MultiArray, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()
