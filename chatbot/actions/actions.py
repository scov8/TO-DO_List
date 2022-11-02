# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset

class TaskSubmit(Action):
    
    def name(self) -> Text:
        return "task_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")
        purpose = tracker.get_slot("purpose")

        print("\n\nSono in TaskSubmit:")
        print("Hour:",hour)
        print("Category:",category)
        print("Task:",task)
        print("Purpose:",purpose)

        if(purpose=="purpose-add"):
            dispatcher.utter_message(text=f"Thanks, you want to add a new task, and the task is: \"{task}\" at {hour} in the category \"{category}\"\nWould you like to confirm?") 
        if(purpose=="purpose-del"):
            dispatcher.utter_message(text=f"Oh no, you want to delete a task, and the task is: \"{task}\" at {hour} in the category \"{category}\"\nWould you like to confirm?") 
        if(purpose=="purpose-update"):
            dispatcher.utter_message(text=f"Ok, you want to modify a task, and the task is: \"{task}\" at {hour} in the category \"{category}\"\nTell me the new task, category or hour?") 

        return []

class ResetSlot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        print("reset slot")
        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        if(task is not None and hour is not None and category is not None):
            dispatcher.utter_message("Ok I deleted your task!")
        else:
            dispatcher.utter_message("What?")

        return [SlotSet("task", None),SlotSet("category", None),SlotSet("hour", None)]
    
class AddToDb(Action):

    def name(self):
        return "action_add_to_db"

    def run(self, dispatcher, tracker, domain):
        print("add to db")
        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        if(task is not None and hour is not None and category is not None):
            dispatcher.utter_message("Ok I added your task!")
            #fare query al db
        else:
            dispatcher.utter_message("What?")

        return [SlotSet("task", None),SlotSet("category", None),SlotSet("hour", None)]