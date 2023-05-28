import requests
from datetime import date
from .config import AppConfig

API_KEY = AppConfig.HOLIDAY_API_KEY


def get_holidays(country_code):
    today = date.today()
    year = today.year
    url = f'https://calendarific.com/api/v2/holidays?api_key={API_KEY}&country={country_code}&year={year}&month={today.month}&day={today.day}'
    response = requests.get(url)
    if response.status_code == 200:
        holidays = response.json()
        return holidays
    else:
        raise Exception("Failed to fetch holidays")


def get_exchange_rates():
    api_key = AppConfig.OPEN_EXCHANGE_RATES_API_KEY
    base_currency = 'USD'
    url = f"https://openexchangerates.org/api/latest.json?app_id={api_key}&base={base_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch exchange rates.")


class WeatherServiceException(Exception):
    pass


class NoInfoException(Exception):
    pass


class WeatherService:
    GEO_URL = 'https://geocoding-api.open-meteo.com/v1/search'
    WEATHER_URL = 'https://api.open-meteo.com/v1/forecast'
    SUN_URL = ''
    @staticmethod
    def get_geo_data(city_name):
        params = {
            'name': city_name
        }
        res = requests.get(f'{WeatherService.GEO_URL}', params=params)
        if res.status_code != 200:
            raise WeatherServiceException('Cannot get geo data')
        elif not res.json().get('results'):
            raise WeatherServiceException('City not found')
        return res.json().get('results')

    @staticmethod
    def get_current_weather_by_geo_data(lat, lon):
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True
        }

        res = requests.get(f'{WeatherService.WEATHER_URL}', params=params)
        if res.status_code != 200:
            raise WeatherServiceException('Cannot get geo data')
        return res.json().get('current_weather')

    @staticmethod
    def get_sun_data(lat, lon):
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lon={lon}"
        response = requests.get(url)
        if response.status_code == 200:
            sun_data = response.json()
            return sun_data
        else:
            raise Exception("Failed to fetch sun data")
