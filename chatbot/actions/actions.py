# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class FullTaskSubmit(Action):
    
    def name(self) -> Text:
        return "full_task_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        print("Sono in FullTaskSubmit:")

        print("\nHour:",hour)
        print("Category:",category)
        print("Task:",task)

        dispatcher.utter_message(text=f"This is the address: {hour} {category} {task}") 
        dispatcher.utter_message(text= f"{hour}")
        dispatcher.utter_message(text= f"{category}")
        dispatcher.utter_message(text= f"{task}")

        return []

class TaskWithHourSubmit(Action):

    def name(self) -> Text:
        return "task_with_hour_submit"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print('Sono in TaskWithHourSubmit')
        
        hour = tracker.get_slot("hour")
        task = tracker.get_slot("task")

        print("\nHour:",hour)
        print("Task:",task)
        
        
        return[]


class TaskWithCategorySubmit(Action):

    def name(self) -> Text:
        return "task_with_category_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        category = tracker.get_slot("category")
        task = tracker.get_slot("task")
        
        print("Sono in TaskWithCategorySubmit:")
        
        print("Category:",category)
        print("Task:",task)


        return []

class TaskOnlySubmit(Action):

    def name(self) -> Text:
        return "task_only_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        task = tracker.get_slot("task")

        print("Sono in TaskOnlySubmit:")
        
        print("Task:",task)


        return []

class HourSubmit(Action):

    def name(self) -> Text:
        return "hour_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hour = tracker.get_slot("hour")

        print("Sono in HourSubmit:")
        print("Hour:",hour)

        return []

class CategorySubmit(Action):

    def name(self) -> Text:
        return "category_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        category = tracker.get_slot("category")

        print("Sono in CategorySubmit:")
        print("Category:",category)

        return []

class HourAndCategorySubmit(Action):

    def name(self) -> Text:
        return "hour_and_category_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        category = tracker.get_slot("category")
        hour = tracker.get_slot("hour")

        print("Sono in HourAndCategorySubmit:")
        
        print("Category:",category)
        print("Hour:",hour)

        return []