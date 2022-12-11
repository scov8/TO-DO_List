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
from std_msgs.msg import String, Bool
from rasa_ros.srv import Dialogue, DialogueResponse


class TerminalInterface:
    '''Class implementing a terminal i/o interface. 

    Methods
    - get_text(self): return a string read from the terminal
    - set_text(self, text): prints the text on the terminal

    '''
    def __init__(self, pub, sub_rec, sub_det, new_person):
        self.pub = pub
        self.sub_rec = sub_rec
        self.sub_det = sub_det
        self.new_person = new_person

    def get_text(self):
        print("Waiting the speech...")
        txt = rospy.wait_for_message("voice_txt", String)
        print("[IN]: ", txt.data)
        return str(txt.data)

    def set_text(self,text):
        data_to_send = String()
        data_to_send.data = text
        self.pub.publish(data_to_send)
        print("[OUT]:", text)
    
    def set_name(self):
        name = rospy.wait_for_message("recognition", String)
        msg = String()
        if name.data != '000#@':
            # self.name = name.data
            self.pub.publish(name)
        else:
            # self.name = None
            msg.data = 'I do not recognize you. Please, can tell me your name?'
            self.pub.publish(msg)
            print("[OUT]:", msg.data)
            name = String(self.get_text())
            self.new_person.publish(name)
            # aspetta il rilascio del mutex
        print("[OUT]: Hi", name.data)
        print('END STARTUP')
    
    def there_is_someone(self):
        global START_UP
        print('IN THERE IS SOMEONE')
        detect  = rospy.wait_for_message("detection", Bool)
        if not START_UP:
            START_UP = True 
        return detect.data

START_UP = True
def main():
    global START_UP
    rospy.init_node('writing')
    rospy.wait_for_service('dialogue_server')
    dialogue_service = rospy.ServiceProxy('dialogue_server', Dialogue)

    pub = rospy.Publisher('bot_answer', String, queue_size=10)
    new_person = rospy.Publisher('new_person', String, queue_size=10)

    sub_rec = rospy.Subscriber('recognition', String, queue_size=10)
    sub_det = rospy.Subscriber('detection', Bool, queue_size=10)

    terminal = TerminalInterface(pub, sub_rec, sub_det, new_person)
    
    while not rospy.is_shutdown():
        if START_UP:
            terminal.set_name()
            START_UP = False
        message = terminal.get_text()
        if message == 'exit': 
            break
        try:
            bot_answer = dialogue_service(message)
            terminal.set_text(bot_answer.answer)
        except rospy.ServiceException as e:
            print("Service call failed: %s" % e)
        
        terminal.there_is_someone()

if __name__ == '__main__':
    try: 
        main()
    except rospy.ROSInterruptException:
        pass