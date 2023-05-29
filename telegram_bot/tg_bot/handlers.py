import json
import requests
from .services import WeatherService, WeatherServiceException, NoInfoException, get_exchange_rates, get_holidays
from .database import add_contact, get_contact, delete_contact, display_contacts
from .config import AppConfig

BOT_TOKEN = AppConfig.BOT_TOKEN
TG_BASE_URL = AppConfig.TG_BASE_URL


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

        match str(self.text.split()[0]).lower():

            case 'holiday':
                if len(self.text.split()) < 2:
                    self.send_message("Please specify the country code.")
                else:
                    try:
                        country_code = self.text.split()[1]
                        holidays = get_holidays(country_code)
                        if holidays and holidays['response']['holidays']:
                            holiday_list = []
                            for holiday in holidays['response']['holidays']:
                                name = holiday['name']
                                description = holiday['description']
                                holiday_info = f"Name: {name}\nDescription: {description}\n"
                                holiday_list.append(holiday_info)
                            holiday_text = "\n".join(holiday_list)
                            self.send_message(holiday_text)
                        else:
                            self.send_message("There are no holidays in this country today.")
                    except Exception as e:
                        self.send_message(f"An error occurred while retrieving holidays: {str(e)}")

            case 'weather':
                city = ''
                if len(self.text.split()) < 2:
                    self.send_message("Please specify the name of the city.")
                else:
                    city = self.text.split()[1]
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
                                {'type': 'weather', 'lat': item.get('latitude'), 'lon': item.get('longitude')})
                        }
                        buttons.append([test_button])
                    markup = {
                        'inline_keyboard': buttons
                    }
                    self.send_markup_message('Choose a city from a list:', markup)

            case 'sun_data':
                city = ''
                if len(self.text.split()) < 2:
                    self.send_message("Please specify the name of the city.")
                else:
                    city = self.text.split()[1]
                try:
                    geo_data = WeatherService.get_geo_data(city)
                except Exception as wse:
                    self.send_message(str(wse))
                else:
                    buttons = []
                    for item in geo_data:
                        test_button = {
                            'text': f'{item.get("name")} - {item.get("admin1")} in {item.get("country")}',
                            'callback_data': json.dumps(
                                {'type': 'sun_data', 'lat': item.get('latitude'), 'lon': item.get('longitude')})
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
                        name = str(self.text.split()[1]).title()
                        contact = vars(get_contact(self.user.id, name))
                        print(type(contact))
                        if contact:
                            self.send_message(f"Name: {contact['name']}, Phone Number: {contact['phone']}")
                        else:
                            self.send_message("Contact not found.")
                    except Exception:
                        self.send_message("Contact not found.")

            case 'delete_contact':
                if len(self.text.split()) < 2:
                    self.send_message("Please specify the name of the contact.")
                else:
                    try:
                        name = str(self.text.split()[1]).title()
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

            case '/exchange_rate':
                try:
                    exchange_rates = get_exchange_rates()
                    output = "Exchange rate:\n"
                    output += f"1 USD = {round(exchange_rates['rates']['UAH'], 2)} UAH\n"
                    output += f"1 USD = {round(exchange_rates['rates']['EUR'], 2)} EUR\n"
                    output += f"1 USD = {round(exchange_rates['rates']['PLN'], 2)} PLN\n"
                    output += f"1 PLN = {round(exchange_rates['rates']['UAH'] / exchange_rates['rates']['PLN'], 2)} UAH\n"
                    output += f"1 EUR = {round(exchange_rates['rates']['UAH'] / exchange_rates['rates']['EUR'], 2)} UAH\n"

                    self.send_message(output)
                except Exception as e:
                    self.send_message(f"An error occurred while retrieving the exchange rate: {str(e)}")

            case '/commands':
                command_list = [
                    "holiday - Country code to display which holidays are celebrated in the world today",
                    "weather  - And city name to display current weather",
                    "sun_data - And city name to display sunrise and sunset information",
                    "add_contact - Add a contact(name and phone number)",
                    "get_contact - Get a contact (name)",
                    "delete_contact - Delete a contact (name)",
                    "/display_contacts - Display all contacts",
                    "/commands - Display available commands",
                    "/exchange_rate - Display exchange rate"
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

    def format_sun_data(self, sun_data):
        sunrise = sun_data['results']['sunrise']
        zenith = sun_data['results']['solar_noon']
        sunset = sun_data['results']['sunset']
        daylight_duration = sun_data['results']['day_length']

        output = f"🌅️  Sunrise: {sunrise}\n"
        output += f"☀️ Solar Noon: {zenith}\n"
        output += f"🌥️  Sunset: {sunset}\n"
        output += f"⏱️ Daylight Duration: {daylight_duration}\n"

        return output

    def handle(self):
        callback_type = self.callback_data.pop('type')
        match callback_type:
            case "weather":
                try:
                    weather = WeatherService.get_current_weather_by_geo_data(**self.callback_data)
                except WeatherServiceException as wse:
                    self.send_message(str(wse))
                else:
                    formatted_weather = self.format_weather_output(weather)
                    self.send_message(formatted_weather)

            case 'sun_data':
                try:
                    sun_data = WeatherService.get_sun_data(**self.callback_data)
                except Exception as e:
                    self.send_message(f"An error occurred while retrieving sun data: {str(e)}")
                else:
                    formatted_sun_data = self.format_sun_data(sun_data)
                    self.send_message(formatted_sun_data)
