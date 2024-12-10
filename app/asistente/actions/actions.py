# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from pymongo import MongoClient
import os

connectionString = os.getenv("MONGO_CONNECTIONSTRING")


class ActionResumirPelicula(Action):
    def name(self) -> Text:
        return "action_resumir_pelicula"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        pelicula = tracker.get_slot("pelicula")
        print(pelicula)
        client = MongoClient(connectionString, 27017)
        db = client['filmnet']
        collection = db['peliculas']
        x = collection.find_one({"nombre": pelicula})
        print(x)
        if x:
            resumen = x["resumen"]
        else:
            resumen = "Lo siento esa no la tenemos"
        client.close()
        dispatcher.utter_message(text=resumen)
        return []
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
