import json
from pprint import pprint
import requests
from .services import WeatherService, WeatherServiceException, NoInfoException
from .database import add_contact, get_contact, delete_contact, display_contacts
from .config import AppConfig

BOT_TOKEN = AppConfig.BOT_TOKEN
TG_BASE_URL = AppConfig.TG_BASE_URL
WEATHER_TYPE = 'weather'


class User:
    def __init__(self, id, is_bot, first_name, last_name, username, language_code):
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code


class TelegramHandler:
    user = None

    def send_markup_message(self, text, markup):
        data = {
            'chat_id': self.user.id,
            'text': text.upper(),
            'reply_markup': markup
        }

        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/sendMessage', json=data)

    def send_message(self, text):
        data = {
            'chat_id': self.user.id,
            'text': text
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/sendMessage', json=data)


class MessageHandler(TelegramHandler):

    def __init__(self, data):
        self.user = User(**data.get('from'))
        self.text = data.get('text')

    def handle(self):

        match self.text.split()[0]:
            case WEATHER_TYPE, city:
                try:
                    geo_data = WeatherService.get_geo_data(city)
                except WeatherServiceException as wse:
                    self.send_message(str(wse))
                else:
                    buttons = []
                    for item in geo_data:
                        test_button = {
                            'text': f'{item.get("name")} - {item.get("admin1")} in {item.get("country")}',
                            'callback_data': json.dumps(
                                {'type': WEATHER_TYPE, 'lat': item.get('latitude'), 'lon': item.get('longitude')})
                        }
                        buttons.append([test_button])
                    markup = {
                        'inline_keyboard': buttons
                    }
                    self.send_markup_message('Choose a city from a list:', markup)
            case 'add_contact':
                if len(self.text.split()) < 3:
                    self.send_message("Please specify the name and phone number of the contact.")
                else:
                    try:
                        name, phone = self.text.split()[1:]
                        add_contact(self.user.id, name, phone)
                        self.send_message("Contact added successfully.")
                    except Exception as e:
                        self.send_message(f"An error occurred while adding the contact: {str(e)}")
            case 'get_contact':
                if len(self.text.split()) < 2:
                    self.send_message("Please specify the name of the contact.")
                else:
                    try:
                        name = self.text.split()[1]
                        contact = get_contact(self.user.id, name)
                        if contact:
                            self.send_message(f"Name: {contact['name']}, Phone Number: {contact['phone']}")
                        else:
                            self.send_message("Contact not found.")
                    except Exception as e:
                        self.send_message(f"An error occurred while retrieving the contact: {str(e)}")
            case 'delete_contact':
                if len(self.text.split()) < 2:
                    self.send_message("Please specify the name of the contact.")
                else:
                    try:
                        name = self.text.split()[1]
                        contact = get_contact(self.user.id, name)
                        if contact:
                            delete_contact(self.user.id, name)
                            self.send_message("Contact deleted successfully.")
                        else:
                            self.send_message("Contact not found.")
                    except Exception as e:
                        self.send_message(f"An error occurred while deleting the contact: {str(e)}")
            case '/display_contacts':
                try:
                    contacts = display_contacts(self.user.id)
                except NoInfoException as wse:
                    self.send_message(str(wse))
                else:
                    if contacts:
                        contact_list = "\n".join(
                            f"Name: {name}, Phone Number: {phone}" for name, phone in contacts.items())
                        self.send_message(contact_list)
                    else:
                        self.send_message("No contacts found.")
            case '/commands':
                print(self.text.split())
                command_list = [
                    "weather  - Display current weather",
                    "add_contact - Add a contact",
                    "get_contact - Get a contact",
                    "delete_contact - Delete a contact",
                    "/display_contacts - Display all contacts",
                    "/commands - Display available commands"
                ]
                command_list_text = "\n".join(command_list)
                self.send_message(command_list_text)


class CallbackHandler(TelegramHandler):

    def __init__(self, data):
        self.user = User(**data.get('from'))
        self.callback_data = json.loads(data.get('data'))

    def format_weather_output(self, weather):
        temperature = weather['temperature']
        winddirection = weather['winddirection']
        windspeed = weather['windspeed']

        output = f"Temperature: {temperature}°C \n"
        output += f"Wind direction: {winddirection}° \n"
        output += f"Wind speed: {windspeed}m/s \n"

        return output

    def handle(self):
        callback_type = self.callback_data.pop('type')
        match callback_type:
            case WEATHER_TYPE:
                try:
                    weather = WeatherService.get_current_weather_by_geo_data(**self.callback_data)
                except WeatherServiceException as wse:
                    self.send_message(str(wse))
                else:
                    formatted_weather = self.format_weather_output(weather)
                    self.send_message(formatted_weather)
