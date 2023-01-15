#!/usr/bin/python3
import rospy
from std_msgs.msg import String, Bool
from pepper_nodes.srv import Text2Speech
from std_msgs.msg import Bool
import time

def main():
    print('starting tts client')
    rospy.init_node('speaking_node')
    rospy.wait_for_service('/tts')
    tts_service = rospy.ServiceProxy('/tts', Text2Speech)
    syn_speech = rospy.Publisher('speaking', Bool, queue_size=1)

    while not rospy.is_shutdown():
        txt = rospy.wait_for_message("bot_answer", String)
        tts_service(txt.data)
        time.sleep(1)
        syn_speech.publish(False)

if __name__ == '__main__':
    try: 
        main()
    except rospy.ROSInterruptException:
        pass