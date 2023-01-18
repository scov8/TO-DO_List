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

from utils import Session
from optparse import OptionParser
import rospy
from pepper_nodes.srv import WakeUp, Rest

'''
This class implements a ROS node used to controll the Pepper posture
'''
class WakeUpNode:
    
    '''
    The costructor creates a session to Pepper and inizializes the services
    '''
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.session = Session(ip, port)
        self.motion_proxy = self.session.get_service("ALMotion")
        self.posture_proxy = self.session.get_service("ALRobotPosture")
    
    '''
    This method calls the ALMotion service and sets the robot to rest position
    '''
    def rest(self, *args):
        try:
            self.motion_proxy.rest()
        except:
            self.motion_proxy = self.session.get_service("ALMotion")
            self.motion_proxy.rest()
        return "ACK"
    
    '''
    This method calls the ALMotion and ALRobotPosture services and it sets motors on and then it sets the robot posture to initial position
    '''
    def wakeup(self, *args):
        try:
            self.motion_proxy.wakeUp()
            self.stand()
        except:
            self.motion_proxy = self.session.get_service("ALMotion")
            self.posture_proxy = self.session.get_service("ALRobotPosture")
            self.motion_proxy.wakeUp()
            self.stand()         

        return "ACK"   
    
    '''
    This method sets the robot posture to "StandInit" posture
    '''
    def stand(self, *args):
        self.posture_proxy.goToPosture("StandInit", 0.5)
    
    '''
    Starts the node and wake up the robot
    '''
    def start(self):
        rospy.init_node("wakeup_node")
        self.wakeup()
        self.stand()   
        #self.rest()    
        rospy.Service("wakeup", WakeUp, self.wakeup)
        rospy.Service("rest", Rest, self.rest)
        rospy.spin()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="192.168.1.18")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        node = WakeUpNode(options.ip, int(options.port))
        rospy.on_shutdown(node.rest)
        node.start()
    except rospy.ROSInterruptException:
        pass
