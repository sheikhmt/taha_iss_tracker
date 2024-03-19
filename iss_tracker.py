#!/usr/bin/env python3

import time
from astropy import coordinates as coord
from astropy import units as u
from astropy.time import Time
import requests
import xmltodict
import pprint
import logging
from datetime import datetime
import math
from flask import Flask, request, jsonify

from geopy.geocoders import Nominatim

app = Flask(__name__)


'''
Utility Functions:
'''

def calculate_speed(x_velocity: float, y_velocity: float, z_velocity: float) -> float:
    """
    Calculates the magnitude of velocity (speed) given its components in three dimensions.

    Args:
        x_velocity (float): The velocity component along the x-axis.
        y_velocity (float): The velocity component along the y-axis.
        z_velocity (float): The velocity component along the z-axis.

    Returns:
        float: The magnitude of velocity (speed) calculated using the Euclidean distance formula.
    """
    speed = math.sqrt(x_velocity ** 2 + y_velocity ** 2 + z_velocity ** 2)
    return speed

def fetch_iss_data() -> bytes:
    """
    Fetches International Space Station (ISS) coordinates data from a public API provided by NASA.

    Returns:
        bytes: The raw XML data downloaded from the API.
    """
    response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    status_code = response.status_code

    if status_code == 200:
        logger.info("Successfully fetched data")
    else:
        logger.error("Failed to fetch data")
        return None

    full_data_xml = response.content

    return full_data_xml

def parse_xml_data(full_data_xml: bytes) -> dict:
    """
    Parses XML data into a dictionary format.

    Args:
        full_data_xml (bytes): The raw XML data as bytes.

    Returns:
        dict: The XML data converted to a dictionary.
    """
    full_data_dicts = xmltodict.parse(full_data_xml)
    return full_data_dicts

def extract_state_vector(xml_data: bytes) -> list:
    """
    Extracts state vector information from XML data.

    Args:
        xml_data (bytes): The raw XML data containing ISS position and velocity information.

    Returns:
        list: A list of dictionaries, each representing the state vector of the ISS at different epochs.
    """
    full_data_dicts = parse_xml_data(xml_data)
    state_vector = full_data_dicts['ndm']['oem']['body']['segment']['data']['stateVector']
    return state_vector

def get_location_info(epoch: str) -> dict:
    """
    Calculates latitude, longitude, altitude, and geolocation information of the ISS for a specific epoch.

    Args:
        epoch (str): The specific epoch time to retrieve location information for.

    Returns:
        dict: A dictionary containing the latitude, longitude, altitude, and geolocation information.
    """
    data = extract_state_vector(fetch_iss_data())
    sv = None
    for item in data:
        if item["EPOCH"] == epoch:
            sv = item

    if sv is None:
        return "Epoch not found, please enter a valid epoch value"

    x = float(sv['X']['#text'])
    y = float(sv['Y']['#text'])
    z = float(sv['Z']['#text'])

    this_epoch = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(sv['EPOCH'][:-5], '%Y-%jT%H:%M:%S'))

    cartrep = coord.CartesianRepresentation([x, y, z], unit=u.km)
    gcrs = coord.GCRS(cartrep, obstime=this_epoch)
    itrs = gcrs.transform_to(coord.ITRS(obstime=this_epoch))
    loc = coord.EarthLocation(*itrs.cartesian.xyz)
    latitude = loc.lat.value
    longitude = loc.lon.value
    altitude = loc.height.value

    geocoder = Nominatim(user_agent='iss_tracker')
    geoloc = geocoder.reverse((latitude, longitude), zoom=15, language='en')

    response_data = {
        'latitude': latitude,
        'longitude': longitude,
        'altitude': altitude,
        'geolocation': str(geoloc)
    }

    return response_data


def epoch_speed(epoch: str) -> str:
    """
    Retrieves the speed of the ISS for a specific epoch.

    Args:
        epoch (str): The epoch for which the ISS speed is requested.

    Returns:
        str: The speed of the ISS for the specified epoch, or an error message if the epoch was not found.
    """

    data = extract_state_vector(fetch_iss_data())
    for item in data:
        if item["EPOCH"] == epoch:
            x_velocity = float(item['X_DOT']['#text'])
            y_velocity = float(item['Y_DOT']['#text'])
            z_velocity = float(item['Z_DOT']['#text'])
            speed = calculate_speed(x_velocity, y_velocity, z_velocity)
            return str(speed)

    return "Epoch not found"

def closest_datapoint_to_now(iss_data: bytes, current_date_and_time: datetime) -> int:
    """
    Calculates the closest data point to the current time from the ISS data.

    Args:
        iss_data (bytes): The raw XML data containing ISS state vectors.
        current_date_and_time (datetime): The current date and time.

    Returns:
        int: The index of the closest data point within the state vector.
    """
    state_vector = extract_state_vector(iss_data)

    year_first_day = datetime(current_date_and_time.year, 1, 1)
    current_date = current_date_and_time.date()
    current_hour = int(str(current_date_and_time)[11:13])
    current_min = int(str(current_date_and_time)[14:16])

    days_since_start_of_year = int((current_date_and_time - year_first_day).days)
    current_day = days_since_start_of_year + 1

    list_of_minutes = []
    
    for instance in state_vector:
        epoch_string = instance['EPOCH']
        day_number = int(epoch_string[5:8])
        hour = int(epoch_string[9:11])
        minute = int(epoch_string[12:14])

        if day_number == current_day:
            if hour == current_hour:
                list_of_minutes.append({'minute_val':minute, 'index':state_vector.index(instance)})

    closest_value_index = None
    min_difference = float('inf')

    for value in list_of_minutes:
        min_in_list = value['minute_val']
        index_of_min_in_list = value['index']
        difference = abs(min_in_list - current_min)
        if difference < min_difference:
            min_difference = difference
            closest_value_index = index_of_min_in_list

    return closest_value_index


'''
Routes:
'''

@app.route('/epochs', methods=['GET'])
def get_epochs():
    """
    Retrieves ISS coordinates data for a specified range of epochs.
    Query parameters:
        offset (int): The starting index of the data to be returned (default is 0).
        limit (int): The maximum number of data points to be returned (default is the length of the data).
    """

    data = extract_state_vector(fetch_iss_data())
    
    offset = request.args.get('offset', 0)
    try:
        offset = int(offset)
    except ValueError:
        return "Invalid start parameter; start must be an integer.\n"

    limit = request.args.get('limit', len(data))

    try:
        limit = int(limit)
    except ValueError:
        return "Invalid limit parameter; limit must be an integer.\n"
    
    result = []
    for item in data[offset:offset+limit]:
        result.append(item)
    
    return jsonify(result)

@app.route('/comment', methods=['GET'])
def get_comment():
    '''
    Prints comment string from data
    '''
    full_data_dicts = parse_xml_data(fetch_iss_data())
    comment = full_data_dicts['ndm']['oem']['body']['segment']['data']['COMMENT']
    return comment

@app.route('/header', methods=['GET'])
def get_header():
    '''
    Prints header string
    '''
    
    full_data_dicts = parse_xml_data(fetch_iss_data())
    header = full_data_dicts['ndm']['oem']['header']
    return header

@app.route('/metadata', methods=['GET'])
def get_metadata():
    '''
    Prints metadata string
    '''
    full_data_dicts = parse_xml_data(fetch_iss_data())
    metadata = full_data_dicts['ndm']['oem']['body']['segment']['metadata']
    return metadata

@app.route('/epochs/<epoch>', methods=['GET'])
def get_specific_epoch(epoch):
    """
    Retrieves ISS coordinates data for a specific epoch.
    """

    data = extract_state_vector(fetch_iss_data())
    for item in data:
        if item["EPOCH"] == epoch:
            return jsonify(item)

    return "Epoch not found"

@app.route('/epochs/<epoch>/speed', methods=['GET'])
def get_epoch_speed(epoch):
    '''
    Returns final speed
    '''
    
    speed = epoch_speed(epoch)
    return jsonify({'speed': speed})

@app.route('/epochs/<epoch>/location', methods=['GET'])
def get_epoch_location(epoch):

    '''
    Returns the final location
    '''

    response_data = get_location_info(epoch)
    return jsonify(response_data)

@app.route('/now', methods=['GET'])
def get_now_info():
    """
    Calculates the closest epoch to the current time and the instantaneous speed at that epoch.
    """
    iss_data = fetch_iss_data()
    current_date_and_time = datetime.now()

    closest_value_index = closest_datapoint_to_now(iss_data, current_date_and_time)
    state_vector = extract_state_vector(fetch_iss_data())

    x_dot_inst = float(state_vector[closest_value_index]['X_DOT']['#text'])
    y_dot_inst = float(state_vector[closest_value_index]['Y_DOT']['#text'])
    z_dot_inst = float(state_vector[closest_value_index]['Z_DOT']['#text'])

    speed_inst = str(calculate_speed(x_dot_inst, y_dot_inst, z_dot_inst))
    specific_epoch = str(state_vector[closest_value_index]['EPOCH'])

    location = get_location_info(specific_epoch)
    
    all_info = {'instantaneous_speed': speed_inst, **location}
    
    return jsonify(all_info)


# Configure logging
logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

