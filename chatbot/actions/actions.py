# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionSubmit(Action):
    
    def name(self) -> Text:
        return "action_submit"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hour = tracker.get_slot("hour")
        category = tracker.get_slot("category")
        task = tracker.get_slot("task")

        print("\nHour:",hour)
        print("Category:",category)
        print("Task:",task)
        
        dispatcher.utter_message(text=hour)
        dispatcher.utter_message(text=category)
        dispatcher.utter_message(text=task)
        dispatcher.utter_message(text=f"This is the address: {hour} {category} {task}") 

        return [SlotSet("hour", hour),SlotSet("category", category),SlotSet("category", category)]
