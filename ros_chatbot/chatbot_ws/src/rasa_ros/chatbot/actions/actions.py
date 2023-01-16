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

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from dateutil.parser import parse

import sqlite3

def correct_time(original_time):
    # tomorrow at 8pm --> 2020–09–28T20:00:00.000–07:00
    original_time = str(original_time)
    tmp = original_time.split('T')
    data, time = tmp[0], tmp[1]
    # data = 2020–09–28
    # time 20:00:00.000–07:00
    tmp = data.split('-')
    data = tmp[2] + " " + tmp[1] + " " + tmp[0] 
    tmp = time.split('-')
    time = tmp[0]
    gmt = tmp[1]
    tmp = time.split(':')
    time = tmp[0] + ' and ' + tmp[1] + ' minutes' # otherwise swap ':' with ' '
    return data, time, gmt

def correct_category(original_cat):
    return original_cat.split('-')[-1]

"""
Global variable used for:
- UPDATE:       It is needed to understand whether the user has initiated an update, then to get the user to insert the new data for the change
- ASK_REMINDER: It is needed to ask the user if they want the reminder after an insert or update
- OLD_TASK:     When an update is in progress the old value of task is saved
"""
UPDATE = False
ASK_REMINDER = False
OLD_TASK = None

class TaskSubmit(Action):
    """
    A class for manage the actions of requesting modification, addition, or deletion of a task
    """

    def name(self) -> Text:
        return "task_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Return the initialized slots after if the user make an update, delete or add
        """

        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")
        purpose = tracker.get_slot("purpose")
        user = tracker.get_slot("PERSON")
        
        # if (time!="null"):
        #     hour = str(parse(str(time)).time())
        #     date = str(parse(str(time)).date())

        # If the user want to manage a task but did not tell his own name
        if (user is None):
            dispatcher.utter_message(text=f"You must tell me first your name!")
            return [SlotSet("task", None), SlotSet("category", None), SlotSet("time", "null"), SlotSet("purpose", None)]

        # based on the action to be taken the corresponding message will be sent to chat to notify the user of the action to be taken
        if (purpose == "purpose-add"):
            category = correct_category(category)
            if (time != "null"):
                date, hour, gmt = correct_time(time)
                dispatcher.utter_message(
                    text=f"Thanks, you want to add a new task, and the task is: \"{task}\" at {hour} of {date} in the category \"{category}\"\nWould you like to confirm?")
            else:
                dispatcher.utter_message(
                    text=f"Thanks, you want to add a new task, and the task is: \"{task}\" in the category \"{category}\"\nWould you like to confirm?")
        elif (purpose == "purpose-del"):
            dispatcher.utter_message(
                text=f"Oh no, you want to delete a task, and the task is: \"{task}\"\nWould you like to confirm?")
        elif (purpose == "purpose-update"):
            dispatcher.utter_message(
                text=f"Ok, you want to modify a task, and the task is: \"{task}\"\"\nWould you like to confirm?")
        else:
            # If a purpose is extracted but is not traceable to any synonym
            dispatcher.utter_message(
                text=f"I don't understand the purpose, please can you tell me now?")
            return [SlotSet("purpose", None)]
        return []


class ResetSlot(Action):
    """
    A class for resetting all the slots and global variables
    """

    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        global UPDATE, ASK_REMINDER

        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        if (task is not None and time is not None and category is not None):
            dispatcher.utter_message("Ok.")
        else:
            dispatcher.utter_message("What?")

        UPDATE = False
        ASK_REMINDER = False

        return [SlotSet("task", None), SlotSet("category", None), SlotSet("time", "null"), SlotSet("purpose", None)]


class AddToDb(Action):
    """
    This class is designed either to add, delete or modify the different task provided by the user
    and then apply the changes to the DataBase
    """

    def name(self):
        return "action_add_to_db"

    def __execute_query(self, conn, query, **kwargs):
        """
        Private method used for execute query

        return the cursor of the query
        """
        global UPDATE  # call the global var
        task = kwargs.get('task')
        time = kwargs.get('time')
        category = kwargs.get('category')
        user = kwargs.get('user')

        curs = conn.cursor()
        if (UPDATE is True):  # the parameters, if we are updating the task, are different
            curs.execute(query, [task, time, category, user,
                         OLD_TASK])
        else:
            curs.execute(query, [user, task, time, category])
        conn.commit()
        return curs

    def __find_purpose(self, dispatcher, purpose, task, time, category, user, conn):
        """
        Private method used to split the different operation that the DB can do, based on
        the different kind of purpose send by the user
        """
        global UPDATE, ASK_REMINDER
        query = ""
        if (UPDATE is True):
            query = 'UPDATE ToDoList SET task=:1, time=:2, category=:3, reminder=False WHERE USER=:4 AND task=:5'
            curs = self.__execute_query(
                conn, query, task=task, time=time, category=category, user=user)
            UPDATE = False
            if (curs.rowcount == 0):
                dispatcher.utter_message(
                    "Oh no, you insert a non-existing entry.")
            else:
                dispatcher.utter_message(
                    "Ok, I modified your task")
            if (time != "null"):
                dispatcher.utter_message("Do you want a reminder?")
                ASK_REMINDER = True
        elif (purpose == "purpose-add"):
            try:
                query = 'INSERT INTO ToDoList (user, task, time, category)VALUES (:1, :2, :3, :4)'
                curs = self.__execute_query(
                    conn, query, task=task, time=time, category=category, user=user)
                dispatcher.utter_message("Ok i added your task")
                if(time != "null"):
                    dispatcher.utter_message("Do you want a reminder?")
                    ASK_REMINDER = True
            except:
                dispatcher.utter_message("This entry already exist")
        elif (purpose == "purpose-del"):
            query = 'DELETE FROM ToDoList WHERE user=:1 AND task=:2'
            curs = conn.cursor()
            curs.execute(query, [user,task])
            conn.commit()
            if (curs.rowcount == 0):
                dispatcher.utter_message(
                    "Oh no, you insert a non-existing entry.")
            else:
                dispatcher.utter_message("Ok I deleted your task.")
        elif (purpose == "purpose-update" and UPDATE is False):
            global OLD_TASK
            OLD_TASK = task
            UPDATE = True
            dispatcher.utter_message(
                "Ok tell me what do you want to modify (tell me only category, hour or task).")
        else:
            raise Exception('Invalid operation')

    def run(self, dispatcher, tracker, domain):
        """
        Execute the action 'Add To DB' and after that clean the slots if the user's purpose is to delete a task,
        otherwise return an empty list
        """
        global UPDATE
        conn = sqlite3.connect('../sito/chatbot.db')
        print("Connection to db:", conn)

        user = tracker.get_slot("PERSON")
        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")
        purpose = tracker.get_slot("purpose")

        self.__find_purpose(dispatcher, purpose, task,
                            time, category, user, conn)

        conn.close()
        if ((purpose == 'purpose-update' or purpose == 'purpose-insert') and ASK_REMINDER == True):
            return []
        else:
            return [SlotSet("task", None), SlotSet("category", None), SlotSet("time", "null"), SlotSet("purpose", None)]


class AddReminder(Action):
    """
    A class for adding a reminder to the newly entered or edited task
    """

    def name(self):
        return "action_add_reminder"

    def run(self, dispatcher, tracker, domain):
        conn = sqlite3.connect('../sito/chatbot.db')
        print("Connection to db:", conn)

        user = tracker.get_slot("PERSON")
        task = tracker.get_slot("task")

        query = 'UPDATE ToDoList SET reminder=True WHERE task=:1 AND USER=:2'
        curs = conn.cursor()
        curs.execute(query, [task, user])
        conn.commit()

        conn.close()

        dispatcher.utter_message("Ok I added also a reminder!")

        return [SlotSet("task", None), SlotSet("category", None), SlotSet("time", "null"), SlotSet("purpose", None)]


class ViewList(Action):
    """
    A class to see the list of to-do list
    """

    def name(self):
        return "action_view_list"

    def run(self, dispatcher, tracker, domain):
        conn = sqlite3.connect('../sito/chatbot.db')
        print("Connection to db:", conn)

        user = tracker.get_slot("PERSON")

        if (user is None):
            dispatcher.utter_message(text=f"You must tell me first your name!")
            return []

        query = 'SELECT task, time, category, reminder FROM ToDoList WHERE user=:1 ORDER BY time ASC'
        curs = conn.cursor()
        curs.execute(query, [user])
        conn.commit()
        selectResult = curs.fetchall()
        conn.close()

        tmp = 'task' if len(selectResult) < 2 else 'tasks'
        dispatcher.utter_message(
            text=f"Ok, there are {len(selectResult)} {tmp} in your To-Do List:\n")
        for ii in selectResult:
            if((ii[1]!="null")):
                date, hour, gmt = correct_time(str(ii[1]))
                out = "- " + str(ii[0]) + " at " + str(hour)
                out += " of " + str(date)
                out += " for " + str(ii[2])
                out += " and the reminder is ON " if (
                    ii[3] == 1 or ii[3] is True) else " and the reminder is OFF"
            else:
                out = "- " + str(ii[0])
                out += " for " + str(ii[2])
                out += " and the reminder is ON " if (
                    ii[3] == 1 or ii[3] is True) else " and the reminder is OFF"
            dispatcher.utter_message(text=f"{out}\n")
        return []


class DeleteAll(Action):
    """
    A class to delete the whole list
    """

    def name(self):
        return "action_delete_all"

    def run(self, dispatcher, tracker, domain):
        conn = sqlite3.connect('../sito/chatbot.db')
        print("Connection to db:", conn)

        user = tracker.get_slot("PERSON")

        if(user is None):
            dispatcher.utter_message(text=f"You must tell me first your name!")
            return []

        query = 'DELETE FROM ToDoList WHERE user=:1'
        curs = conn.cursor()
        curs.execute(query, [user])
        conn.commit()
        conn.close()

        dispatcher.utter_message(text=f"Ok, i deleted your list\n")
        return []


class Affirm(Action):
    """
    A class for manage the action "affirm"
    """

    def name(self):
        return "action_affirm"

    def run(self, dispatcher, tracker, domain):
        global ASK_REMINDER

        # If the reminder addition is not to be made then process the addition to the db, otherwise we add the reminder to the added/updated task
        if (ASK_REMINDER is False):
            addToDb = AddToDb()
            addToDb.run(dispatcher, tracker, domain)
        else:
            ASK_REMINDER = False
            addReminder = AddReminder()
            addReminder.run(dispatcher, tracker, domain)
        return []

# We used this contrivance because although the PERSON slot is text type, it is filled in as a list.
# The problem has not yet been solved by RASA, as can be seen from the following topic:
# https://github.com/RasaHQ/rasa/issues/10188
class ChangePerson(Action):
    """
    A class for manage a name, to fix a bug of Rasa
    """

    def name(self):
        return "action_change_person"

    def run(self, dispatcher, tracker, domain):
        user = tracker.get_slot("PERSON")

        if (isinstance(user, list)):
            return[SlotSet("PERSON", user[0]), SlotSet("time", "null")]
        return[SlotSet("time", "null")]
