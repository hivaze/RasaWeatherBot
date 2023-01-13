# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="rasa_weather_app")
WEATHER_URL = "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True&timezone=GMT&daily=temperature_2m_min,temperature_2m_max,weathercode"


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_get_coordinates"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Getting coordinates...")
        city = tracker.get_slot('location')
        try:
            loc = geolocator.geocode(city)
            dispatcher.utter_message(text=f"Coordinates are {(loc.latitude, loc.longitude)}")
            return [SlotSet("coordinates", (loc.latitude, loc.longitude))]
        except Exception as e:
            dispatcher.utter_message(text=f"Could not get coordindates of your city {e}")


class ActionTellWeather(Action):

    def name(self) -> Text:
        return "action_tell_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Getting weather...")

        coords = tracker.get_slot('coordinates')

        req_url = WEATHER_URL.format(lat=coords[0], lon=coords[1])
        print(req_url)

        answer_dict = requests.get(req_url).json()
        dispatcher.utter_message(f"Current temperature: {answer_dict['current_weather']['temperature']}; "
                                 f"Wind speed: {answer_dict['current_weather']['windspeed']} m/s")
        dispatcher.utter_message(f"Temperature tomorrow: {answer_dict['daily']['temperature_2m_min'][1]} (min), "
                                 f"{answer_dict['daily']['temperature_2m_max'][1]} (max)")

        return []
