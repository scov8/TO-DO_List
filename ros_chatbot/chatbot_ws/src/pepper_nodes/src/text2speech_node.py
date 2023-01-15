#!/usr/bin/python3
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
    parser.add_option("--ip", dest="ip", default="192.168.1.65")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        ttsnode = Text2SpeechNode(options.ip, int(options.port))
        ttsnode.start()
    except rospy.ROSInterruptException:
        pass
