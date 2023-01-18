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
    syn_speech = rospy.Publisher('speaking', Bool, queue_size=10)

    while not rospy.is_shutdown():
        txt = rospy.wait_for_message("bot_answer", String)
        if txt.data!="Can you repeat?":
            tts_service(txt.data)
            time.sleep(1)
        syn_speech.publish(False)

if __name__ == '__main__':
    try: 
        main()
    except rospy.ROSInterruptException:
        pass