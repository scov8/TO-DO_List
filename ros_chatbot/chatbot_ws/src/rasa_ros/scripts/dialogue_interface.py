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
from rasa_ros.srv import Dialogue
from pepper_nodes.srv import LoadUrl, ExecuteJS, LoadUrlRequest


class TerminalInterface:
    '''Class implementing a terminal i/o interface. 

    Methods
    - get_text(self): return a string read from the terminal
    - set_text(self, text): prints the text on the terminal

    '''
    def __init__(self, ip):
        self.ip = ip
        self.pub = rospy.Publisher('bot_answer', String, queue_size=10) # Publisher of the RASA answer
        self.sub_rec = rospy.Subscriber('recognition', String, queue_size=1)
        self.sub_det = rospy.Subscriber('detection', Bool, queue_size=1)
        self.new_person = rospy.Publisher('new_person', String, queue_size=10)
        self.tablet_execute_js = rospy.ServiceProxy('execute_js', ExecuteJS)
        self.tablet_load_url = rospy.ServiceProxy('load_url', LoadUrl)

    def get_text(self):
        print("Waiting the speech...")
        txt = None
        while txt is None:
            try:
                txt = rospy.wait_for_message("voice_txt", String, timeout=1)
            except:
                pass
            if not self.there_is_someone():
                return "noPerson"
        try:
            self.tablet_execute_js("location.reload()")
        except:
            pass
        print("[IN]:", txt.data)
        return str(txt.data)

    def set_text(self,text):
        data_to_send = String()
        data_to_send.data = text
        self.pub.publish(data_to_send)
        print("[OUT]:", text)
    
    def set_name(self):
        '''
        Function to allow to take in input the name of the unknown person
        '''
        msg = String()
        msg.data = "There is somebody?"
        self.pub.publish(msg)
        name = rospy.wait_for_message("recognition", String)
        print(name)
        # if name.data != 'unkn0wn':
        #     print("diverso da ukn")
        if name.data == 'unkn0wn':
            msg.data = 'I do not recognize you. Please, can tell me your name?'
            self.pub.publish(msg)
            print("[OUT]:", msg.data)
            name = String(self.get_text())
            self.new_person.publish(name)
        jsFunc ="goToUser('"+ str(name.data) +"', '"+ str(self.ip) +"')"
        try:
            self.tablet_execute_js(jsFunc)
        except:
            pass
        return str(name.data)
    
    def there_is_someone(self):
        '''
        Method to check if inside the frame is a person and 
        '''
        global START_UP
        detect  = rospy.wait_for_message("detection", Bool)
        if not START_UP and not detect.data:
            START_UP = True
        return detect.data

    def load_url(self, url):
        msg = LoadUrlRequest()
        msg.url = url
        resp = self.tablet_load_url(msg)
        rospy.loginfo(resp.ack)
        print(resp)

START_UP = True

def main():
    global START_UP
    rospy.init_node('writing')
    rospy.wait_for_service('dialogue_server')
    dialogue_service = rospy.ServiceProxy('dialogue_server', Dialogue)

    pub_rec = rospy.Publisher('start', Bool, queue_size=1)

    ip = "192.168.1.237" # ip of the machine with web server 192.168.1.237

    terminal = TerminalInterface(ip)
    
    terminal.pub.publish("Hello world!")
    
    url = r"http://192.168.1.237:8888"
    try:
        terminal.load_url(url)
    except:
        pass
    
    while pub_rec.get_num_connections() < 1: continue
    pub_rec.publish(True)

    while not rospy.is_shutdown():
        if START_UP:
            name = terminal.set_name()
            bot_answer = dialogue_service(name)
            terminal.set_text(bot_answer.answer)
            START_UP = False
        message = terminal.get_text()
        if message == 'exit': 
            break
        if message != "noPerson":
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