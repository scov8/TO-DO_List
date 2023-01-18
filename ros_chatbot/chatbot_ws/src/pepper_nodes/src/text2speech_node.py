#!/usr/bin/python3
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

from utils import Session
from pepper_nodes.srv import Text2Speech
from optparse import OptionParser
import rospy
import time

'''
This class implements a ROS node able to call the Text to speech service of the robot
'''
class Text2SpeechNode:
    
    '''
    The costructor creates a session to Pepper and inizializes the services
    '''
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.session = Session(ip, port)
        self.tts = self.session.get_service("ALTextToSpeech")
        self.motion_proxy = self.session.get_service("ALMotion")
        self.posture_proxy = self.session.get_service("ALRobotPosture")
        self.tracker_service = self.session.get_service("ALTracker")
        self.animation_player_service = self.session.get_service("ALAnimationPlayer")
     
    '''
    Rececives a Text2Speech message and call the ALTextToSpeech service.
    The robot will play the text of the message
    '''
    def say(self, msg):
        try:
            self.animation_player_service.run("animations/Stand/Gestures/BodyTalk_10", _async=True) # Explain_8
            self.tts.say(msg.speech)
        except:
            self.session.reconnect()
            self.tts = self.session.get_service("ALTextToSpeech")
            self.tts.say(msg.speech)
        return "ACK"
        
    '''
    Starts the node and create the tts service
    '''
    def start(self):
        rospy.init_node("text2speech_node")
        rospy.Service('tts', Text2Speech, self.say)

        rospy.spin()

if __name__ == "__main__":
    import time
    time.sleep(3)
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.230")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        ttsnode = Text2SpeechNode(options.ip, int(options.port))
        ttsnode.start()
    except rospy.ROSInterruptException:
        pass
