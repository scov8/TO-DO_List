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


from rasa_ros.srv import Dialogue, DialogueResponse

import rospy
import requests


def handle_service(req):
    input_text = req.input_text   

    # Get answer        
    get_answer_url = 'http://localhost:5002/webhooks/rest/webhook'
    message = {
        "sender": 'bot',
        "message": input_text
    }

    r = requests.post(get_answer_url, json=message)
    response = DialogueResponse()
    response.answer = ""
    for i in r.json():
        response.answer += i['text'] + ' ' if 'text' in i else ''

    return response

def main():

    # Server Initialization
    rospy.init_node('dialogue_service')

    s = rospy.Service('dialogue_server',
                        Dialogue, handle_service)

    rospy.logdebug('Dialogue server READY.')
    rospy.spin()


if __name__ == '__main__':
    try: 
        main()
    except rospy.ROSInterruptException as e:
        pass
