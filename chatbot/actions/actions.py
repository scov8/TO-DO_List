# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset

class FullTaskSubmit(Action):
    
    def name(self) -> Text:
        return "full_task_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        print("\n\nSono in FullTaskSubmit:")
        print("Hour:",hour)
        print("Category:",category)
        print("Task:",task)

        dispatcher.utter_message(text=f"Thanks, your task is: \"{task}\" at {hour} in the category \"{category}\"\nWould you like to confirm?") 

        return []

class TaskWithHourSubmit(Action):

    def name(self) -> Text:
        return "task_with_hour_submit"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print('\nSono in TaskWithHourSubmit')
        
        hour = tracker.get_slot("hour")
        task = tracker.get_slot("task")

        print("Hour:",hour)
        print("Task:",task)

        dispatcher.utter_message(text=f"Your task is \"{task}\" at {hour}, but you missed the category!\nPlease write here the category or modify the hour") 
        
        return[]


class TaskWithCategorySubmit(Action):

    def name(self) -> Text:
        return "task_with_category_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        category = tracker.get_slot("category")
        task = tracker.get_slot("task")
        
        print("\nSono in TaskWithCategorySubmit:")
        
        print("Category:",category)
        print("Task:",task)

        dispatcher.utter_message(text=f"Your task is \"{task}\" in the category {category}, but you missed the hour!\nPlease write here the hour or modify the category") 

        return []

class TaskOnlySubmit(Action):

    def name(self) -> Text:
        return "task_only_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        task = tracker.get_slot("task")

        print("\nSono in TaskOnlySubmit:")
        print("Task:",task)

        dispatcher.utter_message(text=f"Your task is \"{task}\", but you missed the hour and the category!\nPlease write here the hour and the category") 

        return []

class HourSubmit(Action):

    def name(self) -> Text:
        return "hour_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        if(category is not None and task is not None):
            dispatcher.utter_message(text=f"Thanks, your task is: \"{task}\" at {hour} in the category \"{category}\"\nWould you like to confirm?")
        elif (category is None and task is not None):
            dispatcher.utter_message(text=f"Ok I updated your hour in {hour}, please tell me the category now (or change again the hour)!")
        else:
            dispatcher.utter_message(text=f"You tell me only the hour, what do you want?")

        print("\nSono in HourSubmit:")
        print("Hour:",hour)

        return []

class CategorySubmit(Action):

    def name(self) -> Text:
        return "category_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        if(hour is not None and task is not None):
            dispatcher.utter_message(text=f"Thanks, your task is: \"{task}\" at {hour} in the category \"{category}\"\nWould you like to confirm?")
        elif (hour is None and task is not None):
            dispatcher.utter_message(text=f"Ok I updated your category in {category}, please tell me the hour now (or change again the category)!")
        else:
            dispatcher.utter_message(text=f"You tell me only the category and hour, what do you want?")


        print("\nSono in CategorySubmit:")
        print("Category:",category)

        return []

class HourAndCategorySubmit(Action):

    def name(self) -> Text:
        return "hour_and_category_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        if(task is not None):
            dispatcher.utter_message(text=f"Thanks, your task is: \"{task}\" at {hour} in the category \"{category}\"\nWould you like to confirm?")
        else:
            dispatcher.utter_message(text=f"You tell me only the category and hour, what do you want?")

        print("\nSono in HourAndCategorySubmit:")
        
        print("Category:",category)
        print("Hour:",hour)

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