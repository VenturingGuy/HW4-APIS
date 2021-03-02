import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        # TODO: Enter query parameters here for the 'appid' (your api key),
        # the city, and the units (metric or imperial).
        # See the documentation here: https://openweathermap.org/current
        'q': city,
        'appid': '8dc260bebb36d0633ea80322c7425314',
        'units': 'imperial'

    }

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    pp.pprint(result_json)
    print(result_json)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.

    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()` 
    # function.
    context = {
        'date': datetime.now(),
        'city': city,
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)

def helper_function(city, units):
    params = {
        'q': city,
        'appid': '8dc260bebb36d0633ea80322c7425314',
        'units': units
    }

    result_json = requests.get(API_URL, params=params).json()
    return result_json



@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this!

    city1_results = helper_function(city1, units)
    city2_results = helper_function(city2, units)


    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    city_info = {
        'date': datetime.now(),
        'units_letter': get_letter_for_units(units),
        'city1_info': {
            'city': city1,
            'description': city1_results['weather'][0]['description'],
            'temp': city1_results['main']['temp'],
            'humidity': city1_results['main']['humidity'],
            'wind_speed': city1_results['wind']['speed'],
            'sunrise': datetime.fromtimestamp(city1_results['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(city1_results['sys']['sunset']),
        },
        'city2_info': {
            'city': city2,
            'description': city2_results['weather'][0]['description'],
            'temp': city2_results['main']['temp'],
            'humidity': city2_results['main']['humidity'],
            'wind_speed': city2_results['wind']['speed'],
            'sunrise': datetime.fromtimestamp(city2_results['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(city2_results['sys']['sunset']),
        }
    }

    temp_diff = 0
    temp_output = ''
    humid_diff = 0
    humid_output = ''
    wind_diff = 0
    wind_output = ''
    sun_diff = 0
    sun_output = ''

    if (city_info['city1_info']['temp'] > city_info['city2_info']['temp']):
        temp_diff = city_info['city1_info']['temp'] - city_info['city2_info']['temp']
        temp_output = "warmer"
    else:
        temp_diff = city_info['city2_info']['temp'] - city_info['city1_info']['temp']
        temp_output = "colder"
    
    if (city_info['city1_info']['humidity'] > city_info['city2_info']['humidity']):
        humid_diff = city_info['city1_info']['humidity'] - city_info['city2_info']['humidity']
        humid_output = "greater"
    else:
        humid_diff = city_info['city2_info']['humidity'] - city_info['city1_info']['humidity']
        humid_output = "less"

    if (city_info['city1_info']['wind_speed'] > city_info['city2_info']['wind_speed']):
        wind_diff = city_info['city1_info']['wind_speed'] - city_info['city2_info']['wind_speed']
        wind_output = "greater"
    else:
        wind_diff = city_info['city2_info']['wind_speed'] - city_info['city1_info']['wind_speed']
        wind_output = "less"

    if (city_info['city1_info']['sunset'] > city_info['city2_info']['sunset']):
        sun_diff = city_info['city1_info']['sunset'] - city_info['city2_info']['sunset']
        sun_output = "earlier"
    else:
        sun_diff = city_info['city2_info']['sunset'] - city_info['city1_info']['sunset']
        sun_output = "later"

    city_output = {
        'temp_diff': round(temp_diff, 2),
        'temp_output': temp_output,
        'humid_diff': humid_diff,
        'humid_output': humid_output,
        'wind_diff': round(wind_diff, 2),
        'wind_output': wind_output,
        'sun_diff': sun_diff,
        'sun_output': sun_output
    }

    context = {}
    context.update(city_info)
    context.update(city_output)

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
