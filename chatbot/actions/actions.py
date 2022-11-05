# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet #, ReminderScheduled, ReminderCancelled
from dateutil.parser import parse

import sqlite3

"""
Global variable used for:
- UPDATE:       It is needed to understand whether the user has initiated an update, then to get the user to insert the new data for the change
- ASKREMINDER:  It is needed to ask the user if they want the reminder after an insert or update
- OLD_TIME:     When an update is in progress the old value of time is saved
- OLD_CATEGORY: When an update is in progress the old value of category is saved
- OLD_TASK:     When an update is in progress the old value of task is saved
"""
UPDATE = False      
ASKREMINDER = False 
OLD_TIME = None     
OLD_CATEGORY = None 
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
        hour = str(parse(str(time)).time())
        date = str(parse(str(time)).date())

        # If the user want to manage a task but did not tell his own name
        if(user is None):
            dispatcher.utter_message(text = f"You must tell me first your name!") 
            return [SlotSet("task", None),SlotSet("category", None),SlotSet("time", None),SlotSet("purpose", None)]

        # based on the action to be taken the corresponding message will be sent to chat to notify the user of the action to be taken
        if (purpose == "purpose-add"):
            dispatcher.utter_message(text = f"Thanks, you want to add a new task, and the task is: \"{task}\" at {hour} of {date} in the category \"{category}\"\nWould you like to confirm?") 
        elif (purpose == "purpose-del"):
            dispatcher.utter_message(text = f"Oh no, you want to delete a task, and the task is: \"{task}\" at {hour} of {date}  in the category \"{category}\"\nWould you like to confirm?") 
        elif (purpose == "purpose-update"):
            dispatcher.utter_message(text = f"Ok, you want to modify a task, and the task is: \"{task}\" at {hour} of {date}  in the category \"{category}\"\nWould you like to confirm?") 
        else:
            # If a purpose is extracted but is not traceable to any synonym
            dispatcher.utter_message(text = f"I don't understand the purpose, please can you tell me now?") 
            return [SlotSet("purpose", None)]

        return []

class ResetSlot(Action):
    """
    A class for resetting all the slots and global variables
    """
    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        global UPDATE, ASKREMINDER

        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        if (task is not None and time is not None and category is not None):
            dispatcher.utter_message("Ok.")
        else:
            dispatcher.utter_message("What?")

        UPDATE = False
        ASKREMINDER=False

        return [SlotSet("task", None),SlotSet("category", None),SlotSet("time", None),SlotSet("purpose", None)]
    
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
        global UPDATE # call the global var
        task = kwargs.get('task')
        time = kwargs.get('time')
        category = kwargs.get('category')
        user = kwargs.get('user')

        curs = conn.cursor()
        if (UPDATE is True): # the parameters, if we are updating the task, are different
            global OLD_TIME, OLD_CATEGORY, OLD_TASK
            curs.execute(query, [task, time, category, user, OLD_TASK, OLD_TIME, OLD_CATEGORY])
        else:
            curs.execute(query, [user, task, time, category])
        conn.commit()
        return curs
    
    def __find_purpose(self, dispatcher, purpose, task, time, category, user, conn):
        """
        Private method used to split the different operation that the DB can do, based on 
        the different kind of purpose send by the user
        """
        global UPDATE, ASKREMINDER

        query = ""
        if (UPDATE is True):
            query = 'UPDATE ToDoList SET task=:1, time=:2, category=:3, reminder=False WHERE USER=:4 AND task=:5 AND time=:6 AND category=:7'
            curs = self.__execute_query(conn, query, task=task, time=time, category=category, user=user)
            UPDATE = False
            if (curs.rowcount == 0):
                dispatcher.utter_message("Oh no, you insert a non-existing entry.")
            else:
                dispatcher.utter_message("Ok, I modified your task, do you want a reminder?")
                ASKREMINDER=True
        elif (purpose == "purpose-add"):
            query = 'INSERT INTO ToDoList (user, task, time, category)VALUES (:1, :2, :3, :4)'
            curs = self.__execute_query(conn, query, task=task, time=time, category=category, user=user)
            dispatcher.utter_message("Ok i added your task, do you want a reminder?")
            ASKREMINDER=True
        elif (purpose == "purpose-del"):
            query = 'DELETE FROM ToDoList WHERE user=:1 AND task=:2 AND time=:3 AND category=:4'
            curs = self.__execute_query(conn, query, task=task, time=time, category=category, user=user)
            if( curs.rowcount == 0):
                dispatcher.utter_message("Oh no, you insert a non-existing entry.")
            else:
                dispatcher.utter_message("Ok I deleted your task.")
        elif (purpose == "purpose-update" and UPDATE is False):
            global OLD_TIME, OLD_CATEGORY, OLD_TASK
            OLD_TIME = time
            OLD_CATEGORY = category
            OLD_TASK = task
            UPDATE = True
            dispatcher.utter_message("Ok tell me what do you want to modify (tell me only category, hour or task).")
        else:
            raise Exception('Invalid operation')

    def run(self, dispatcher, tracker, domain):
        """
        Execute the action 'Add To DB' and after that clean the slots if the user's purpose is to delete a task,
        otherwise return an empty list
        """
        global UPDATE
        conn = sqlite3.connect('../chatbot.db')
        print("Connection to db:", conn)

        user = tracker.get_slot("PERSON")
        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")
        purpose = tracker.get_slot("purpose")

        self.__find_purpose(dispatcher, purpose, task, time, category, user, conn)

        conn.close()
        if (purpose == 'purpose-update' or purpose == 'purpose-insert'):
            return []
        else:
            return [SlotSet("task", None),SlotSet("category", None),SlotSet("time", None),SlotSet("purpose", None)]

class AddReminder(Action):
    """
    A class for adding a reminder to the newly entered or edited task
    """
    def name(self):
        return "action_add_reminder"

    def run(self, dispatcher, tracker, domain):
        conn = sqlite3.connect('../chatbot.db')
        print("Connection to db:", conn)

        user = tracker.get_slot("PERSON")
        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        query = 'UPDATE ToDoList SET reminder=True WHERE task=:1 AND time=:2 AND category=:3 AND USER=:4'
        curs = conn.cursor()
        curs.execute(query, [task, time, category, user])
        conn.commit()

        conn.close()

        dispatcher.utter_message("Ok I added also a reminder!")

        return [SlotSet("task", None),SlotSet("category", None),SlotSet("time", None),SlotSet("purpose", None)]

class ViewList(Action):
    """
    A class to see the list of to-do list
    """
    def name(self):
        return "action_view_list"

    def run(self, dispatcher, tracker, domain):
        conn = sqlite3.connect('../chatbot.db')
        print("Connection to db:", conn)

        user = tracker.get_slot("PERSON")

        if(user is None):
            dispatcher.utter_message(text = f"You must tell me first your name!") 
            return []

        query = 'SELECT task, time, category, reminder FROM ToDoList WHERE user=:1 ORDER BY time ASC'
        curs = conn.cursor()
        curs.execute(query, [user])
        conn.commit()
        selectResult = curs.fetchall()
        conn.close()

        tmp =  'task' if len(selectResult) < 2 else 'tasks'
        dispatcher.utter_message(text = f"Ok, there are {len(selectResult)} {tmp} in your To-Do List:\n") 
        for ii in selectResult:
            out = "- " + str(ii[0]) + " at " + str(parse(str(ii[1])).time()) 
            out += " of "+ str(parse(str(ii[1])).date()) 
            out += " for " + str(ii[2])
            out += " and the reminder is ON " if (ii[3] == 1 or ii[3] is True) else " and the reminder is OFF"
            dispatcher.utter_message(text = f"{out}\n")

        return []

class Affirm(Action):
    """
    A class for manage the action "affirm"
    """
    def name(self):
        return "action_affirm"

    def run(self, dispatcher, tracker, domain):
        global ASKREMINDER

        # If the reminder addition is not to be made then process the addition to the db, otherwise we add the reminder to the added/updated task
        if (ASKREMINDER is False):
            addToDb = AddToDb()
            addToDb.run(dispatcher, tracker, domain)
        else:
            ASKREMINDER = False
            addReminder = AddReminder()
            addReminder.run(dispatcher, tracker, domain)
        return []

