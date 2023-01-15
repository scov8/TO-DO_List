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
from optparse import OptionParser
import rospy
from pepper_nodes.srv import WakeUp, Rest
import qi
import argparse
import sys

'''
This class implements a ROS node used to controll the Pepper posture
'''
class TrackerNode:
    '''
    The costructor creates a session to Pepper and inizializes the services
    '''
    def __init__(self, ip, port, faceSize):
        self.ip = ip
        self.port = port
        self.session = Session(ip, port)
        self.faceSize = faceSize
        self.motion_proxy = self.session.get_service("ALMotion")
        self.posture_proxy = self.session.get_service("ALRobotPosture")
        self.tracker_service = self.session.get_service("ALTracker")
        self.animation_player_service = self.session.get_service("ALAnimationPlayer")
    
    '''
    This method calls the ALMotion service and sets the robot to rest position
    '''
    def stop(self, *args):
        try:
            self.motion_proxy.rest()
            self.tracker_service.stopTracker()
        except:
            self.tracker_service = self.session.get_service("ALTracker") 
            self.tracker_service.stopTracker()
        return "ACK"

    def start(self):
        rospy.init_node("tracker_node")
        self.trackernode()
        rospy.Service("tracker", WakeUp, self.trackernode)
        rospy.spin()
    
    '''
    This method calls the ALMotion and ALRobotPosture services and it sets motors on and then it sets the robot posture to initial position
    '''
    def trackernode(self, *args):
        try:
            # Add target to track.
            targetName = "Face"
            faceWidth = self.faceSize
            self.tracker_service.registerTarget(targetName, faceWidth)
            # Then, start tracker.
            self.tracker_service.track(targetName)
        except:
            self.motion_proxy = self.session.get_service("ALMotion")
            self.posture_proxy = self.session.get_service("ALRobotPosture")
            self.tracker_service = self.session.get_service("ALTracker") 
            self.animation_player_service = self.session.get_service("ALAnimationPlayer")

        return "ACK"   

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="192.168.1.65")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        node = TrackerNode(options.ip, int(options.port), 0.1)
        node.start()
    except rospy.ROSInterruptException:
        node.stop()
