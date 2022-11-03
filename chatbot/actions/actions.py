# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ReminderScheduled, ReminderCancelled
from dateutil.parser import parse
import datetime 

import sqlite3

update = False
askReminder=False
old_time = None
old_category = None
old_task = None

class TaskSubmit(Action):
    
    def name(self) -> Text:
        return "task_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")
        purpose = tracker.get_slot("purpose")

        print("\n\nSono in TaskSubmit:")
        print("time:",time)
        print("Category:",category)
        print("Task:",task)
        print("Purpose:",purpose)

        hour = str(parse(str(time)).time())
        date = str(parse(str(time)).date())

        if (purpose == "purpose-add"):
            dispatcher.utter_message(text = f"Thanks, you want to add a new task, and the task is: \"{task}\" at {hour} of {date} in the category \"{category}\"\nWould you like to confirm?") 
        if (purpose == "purpose-del"):
            dispatcher.utter_message(text = f"Oh no, you want to delete a task, and the task is: \"{task}\" at {hour} of {date}  in the category \"{category}\"\nWould you like to confirm?") 
        if (purpose == "purpose-update"):
            dispatcher.utter_message(text = f"Ok, you want to modify a task, and the task is: \"{task}\" at {hour} of {date}  in the category \"{category}\"\nWould you like to confirm?") 

        return []

class ResetSlot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        print("reset slot")
        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        if (task is not None and time is not None and category is not None):
            dispatcher.utter_message("Ok I deleted your task!")
        else:
            dispatcher.utter_message("What?")

        return [SlotSet("task", None),SlotSet("category", None),SlotSet("time", None),SlotSet("purpose", None)]
    
class AddToDb(Action):
        
    def name(self):
        return "action_add_to_db"
    
    def __find_purpose(self, dispatcher, purpose, task, time, category, user, conn):
        global update, old_time, old_category, old_task, askReminder

        query = ""
        if(update is True):
            query = 'UPDATE ToDoList SET task=:1, time=:2, category=:3 WHERE task=:4 AND time=:5 AND category=:6 AND USER=:7'
            curs = conn.cursor()
            curs.execute(query, [task, time, category, old_task, old_time, old_category, user])
            conn.commit()
            update = False
            if(curs.rowcount==0):
                dispatcher.utter_message("Oh no, you insert a non-existing entry")
            else:
                dispatcher.utter_message("Ok, i modified your task")
        elif (purpose == "purpose-add"):
            query = 'INSERT INTO ToDoList (user, task, time, category)VALUES (:1, :2, :3, :4)'
            curs = conn.cursor()
            curs.execute(query, [user, task, time, category])
            print("curs",curs)
            conn.commit()
            dispatcher.utter_message("Ok i added your task, do you want a reminder?")
            askReminder=True
        elif (purpose == "purpose-del"):
            query = 'DELETE FROM ToDoList WHERE task=:1 AND time=:2 AND category=:3 AND user=:4'
            curs = conn.cursor()
            curs.execute(query, [task, time, category,user])
            print("curs",curs)
            conn.commit()
            dispatcher.utter_message("Ok i deleted your task")
        elif (purpose == "purpose-update" and update is False):
            old_time = time
            old_category = category
            old_task = task
            update = True
            dispatcher.utter_message("Ok tell me what do you want to modify")
        else:
            raise Exception('Invalid operation')

    def run(self, dispatcher, tracker, domain):
        global update
        conn = sqlite3.connect('../chatbot.db')
        print("connessione al db:", conn)

        user = tracker.get_slot("PERSON")
        time = tracker.get_slot("time")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")
        purpose = tracker.get_slot("purpose")

        self.__find_purpose(dispatcher, purpose, task, time, category, user, conn)

        conn.close()
        if ((purpose == 'purpose-update' and update is True) or purpose == 'purpose-insert' ):
            return []
        else:
            return [SlotSet("task", None),SlotSet("category", None),SlotSet("time", None),SlotSet("purpose", None)]

class AddReminder(Action):
    def name(self):
        return "action_add_reminder"

    def run(self, dispatcher, tracker, domain):
        conn = sqlite3.connect('../chatbot.db')
        print("connessione al db:", conn)

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

    def name(self):
        return "action_view_list"

    def run(self, dispatcher, tracker, domain):
        conn = sqlite3.connect('../chatbot.db')
        print("connessione al db:", conn)

        user = tracker.get_slot("PERSON")

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
    def name(self):
        return "action_affirm"

    def run(self, dispatcher, tracker, domain):
        global askReminder

        if(askReminder==False):
            addToDb=AddToDb()
            addToDb.run(dispatcher, tracker, domain)
        else:
            addReminder=AddReminder()
            addReminder.run(dispatcher, tracker, domain)
            askReminder=False

        return []

