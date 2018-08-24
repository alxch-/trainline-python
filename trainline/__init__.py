# -*- coding: utf-8 -*-

"""Top-level package for Trainline."""

import requests
from requests import ConnectionError
import json
from datetime import datetime, timedelta
import pytz

__author__ = """Thibault Ducret"""
__email__ = 'hello@tducret.com'
__version__ = '0.0.1'

_SEARCH_URL = "https://www.trainline.eu/api/v5_1/search"
_DEFAULT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
_BIRTHDATE_FORMAT = '%d/%m/%Y'
_READABLE_DATE_FORMAT = "%d/%m/%Y %H:%M"
_DEFAULT_SEARCH_TIMEZONE = 'Europe/Paris'

ENFANT_PLUS = "ENFANT_PLUS"
JEUNE = "JEUNE"
_AVAILABLE_CARDS = [ENFANT_PLUS, JEUNE]


class Client(object):
    """ Do the requests with the servers """
    def __init__(self):
        self.session = requests.session()
        self.headers = {
                    'Accept': 'application/json',
                    'User-Agent': 'CaptainTrain/43(4302) Android/4.4.2(19)',
                    'Accept-Language': 'fr',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Host': 'www.trainline.eu',
                    }

    def _get(self, url, expected_status_code=200):
        ret = self.session.get(url=url, headers=self.headers)
        if (ret.status_code != expected_status_code):
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret

    def _post(self, url, post_data, expected_status_code=200):
        ret = self.session.post(url=url,
                                headers=self.headers,
                                data=post_data)
        if (ret.status_code != expected_status_code):
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret


class Trainline(object):
    """ Class to... """
    def __init__(self):
        pass

    def search(self, departure_station_id, arrival_station_id, departure_date):
        """ Search on Trainline """
        data = {
              "local_currency": "EUR",
              "search": {
                "passengers": [
                  {
                    "id": "90ec4e55-f6f1-4298-bb02-7dd88fe33fca",
                    "age": 26,
                    "cards": [],
                    "label": "90ec4e55-f6f1-4298-bb02-7dd88fe33fca"
                  }
                ],
                "arrival_station_id": arrival_station_id,
                "departure_date": departure_date,
                "departure_station_id": departure_station_id,
                "systems": [
                  "benerail",
                  "busbud",
                  "db",
                  "hkx",
                  "idtgv",
                  "locomore",
                  "ntv",
                  "ocebo",
                  "ouigo",
                  "ravel",
                  "renfe",
                  "sncf",
                  "timetable",
                  "trenitalia",
                  "westbahn",
                  "flixbus",
                  "pao_ouigo",
                  "pao_sncf",
                  "leoexpress",
                  "city_airport_train",
                  "obb",
                  "distribusion"
                ]
              }
            }
        post_data = json.dumps(data)
        c = Client()
        ret = c._post(url=_SEARCH_URL, post_data=post_data)
        return ret


class Trip(object):
    """ Class to represent a trip, composed of one or more segments """
    def __init__(self, dict):
        expected = {
            "id": str,
            "departure_date": str,
            "departure_station_id": str,
            "arrival_date": str,
            "arrival_station_id": str,
            "price": float,
            "currency": str,
            "segment_ids": list,
            "segments": list,
        }

        for expected_param, expected_type in expected.items():
            param_value = dict.get(expected_param)
            if type(param_value) is not expected_type:
                raise TypeError("Type {} expected for {}, {} received".format(
                    expected_type, expected_param, type(param_value)))
            setattr(self, expected_param, param_value)

        # Remove ':' in the +02:00 offset (=> +0200). It caused problem with
        # Python 3.6 version of strptime
        self.departure_date = _fix_date_offset_format(self.departure_date)
        self.arrival_date = _fix_date_offset_format(self.arrival_date)

        self.departure_date_obj = _str_datetime_to_datetime_obj(
            self.departure_date)
        self.arrival_date_obj = _str_datetime_to_datetime_obj(
            self.arrival_date)

        if self.price < 0:
            raise ValueError("price cannot be < 0, {} received".format(
                self.price))

    def __str__(self):
        return("{} → {} : {} {} ({} segments) [id : {}]".format(
            self.departure_date, self.arrival_date, self.price, self.currency,
            len(self.segment_ids), self.id))

    # __hash__ and __eq__ methods are defined to allow to remove duplicates
    # in the results with list(set(trip_list))
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.id))


class Passenger(object):
    """ Class to represent a passenger """
    def __init__(self, birthdate, cards=[]):
        self.birthdate = birthdate
        self.birthdate_obj = _str_date_to_date_obj(
            str_date=self.birthdate,
            date_format=_BIRTHDATE_FORMAT)

        for card in cards:
            if card not in _AVAILABLE_CARDS:
                raise KeyError("Card '{}' unknown, [{}] available".format(
                    card, ",".join(_AVAILABLE_CARDS)))
        self.cards = cards

    def __str__(self):
        return(repr(self))

    def __repr__(self):
        return("Passenger(birthdate={}, cards=[{}])".format(
            self.birthdate,
            ",".join(self.cards)))


class Segment(object):
    """ Class to represent a segment
    (a trip is composed of one or more segment) """
    def __init__(self, dict):
        expected = {
            "id": str,
            "departure_date": str,
            "departure_station_id": str,
            "arrival_date": str,
            "arrival_station_id": str,
            "transportation_mean": str,
            "carrier": str,
            "train_number": str,
            "travel_class": str,
            "trip_id": str,
            "comfort_class_ids": list,
        }

        for expected_param, expected_type in expected.items():
            param_value = dict.get(expected_param)
            if type(param_value) is not expected_type:
                raise TypeError("Type {} expected for {}, {} received".format(
                    expected_type, expected_param, type(param_value)))
            setattr(self, expected_param, param_value)

        # Remove ':' in the +02:00 offset (=> +0200). It caused problem with
        # Python 3.6 version of strptime
        self.departure_date = _fix_date_offset_format(self.departure_date)
        self.arrival_date = _fix_date_offset_format(self.arrival_date)

        self.departure_date_obj = _str_datetime_to_datetime_obj(
            self.departure_date)
        self.arrival_date_obj = _str_datetime_to_datetime_obj(
            self.arrival_date)

    def __str__(self):
        return("{} → {} : {}({}) ({} comfort_class) [id : {}]".format(
            self.departure_date, self.arrival_date, self.transportation_mean,
            self.carrier,
            len(self.comfort_class_ids), self.id))

    # __hash__ and __eq__ methods are defined to allow to remove duplicates
    # in the results with list(set(trip_list))
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.id))


def _str_datetime_to_datetime_obj(str_datetime,
                                  date_format=_DEFAULT_DATE_FORMAT):
    """ Check the expected format of the string date and returns a datetime
    object """
    try:
        datetime_obj = datetime.strptime(str_datetime, date_format)
    except:
        raise TypeError("date must match the format {}, received : {}".format(
            date_format, str_datetime))
    if datetime_obj.tzinfo is None:
        tz = pytz.timezone(_DEFAULT_SEARCH_TIMEZONE)
        datetime_obj = tz.localize(datetime_obj)
    return datetime_obj


def _str_date_to_date_obj(str_date, date_format=_BIRTHDATE_FORMAT):
    """ Check the expected format of the string date and returns a datetime
    object """
    try:
        date_obj = datetime.strptime(str_date, date_format)
    except:
        raise TypeError("date must match the format {}, received : {}".format(
            date_format, str_date))
    return date_obj


def _fix_date_offset_format(date_str):
    """ Remove ':' in the UTC offset, for example :
    >>> print(_fix_date_offset_format("2018-10-15T08:49:00+02:00"))
    2018-10-15T08:49:00+0200
    """
    return date_str[:-3]+date_str[-2:]


def get_station_id(station_name):
    # TODO : Use trainline station database instead
    # https://github.com/trainline-eu/stations
    # https://raw.githubusercontent.com/trainline-eu/stations/master/stations.csv
    _AVAILABLE_STATIONS = {
        "Toulouse Matabiau": "5311",
        "Bordeaux St-Jean": "828",
    }
    return _AVAILABLE_STATIONS[station_name]


def search(departure_station, arrival_station,
           from_date, to_date, bicyle_required=False, passengers=[],
           transportation_mean=None):
    t = Trainline()

    departure_station_id = get_station_id(departure_station)
    arrival_station_id = get_station_id(arrival_station)

    from_date_obj = _str_datetime_to_datetime_obj(
        from_date, date_format=_READABLE_DATE_FORMAT)

    to_date_obj = _str_datetime_to_datetime_obj(
        to_date, date_format=_READABLE_DATE_FORMAT)

    trip_list = []

    search_date = from_date_obj

    while True:

        last_search_date = search_date
        departure_date = search_date.strftime(_DEFAULT_DATE_FORMAT)

        ret = t.search(
            departure_station_id=departure_station_id,
            arrival_station_id=arrival_station_id,
            departure_date=departure_date)
        j = json.loads(ret.text)
        trips = _get_trips(search_results_obj=j)
        trip_list += trips

        # Check the departure date of the last trip found
        # If it is after the 'to_date', we can stop searching
        if trips[-1].departure_date_obj > to_date_obj:
            break
        else:
            search_date = trips[-1].departure_date_obj
            # If we get a date earlier than the last search date,
            # it means that we may be searching during the night,
            # so we must increment the search_date till we have a
            # trip posterior to 'to_date'
            # Probably the next day in this case
            if search_date <= last_search_date:
                search_date = last_search_date + timedelta(hours=4)
    trip_list = list(set(trip_list))  # Remove duplicate trips in the list

    # Filter the list
    filtered_trip_list = _filter_trips(trip_list,
                                       from_date_obj=from_date_obj,
                                       to_date_obj=to_date_obj,
                                       transportation_mean=transportation_mean)

    # Sort by date
    filtered_trip_list = sorted(filtered_trip_list,
                                key=lambda trip: trip.departure_date_obj)
    return filtered_trip_list


def _convert_date_format(origin_date_str,
                         origin_date_format, target_date_format):
    """ Convert a date string to another format, for example :
    >>> print(_convert_date_format(origin_date_str="01/01/2002 08:00",\
origin_date_format="%d/%m/%Y %H:%M", target_date_format="%Y-%m-%dT%H:%M:%S%z"))
    2002-01-01T08:00:00+0100
    """
    date_obj = _str_datetime_to_datetime_obj(str_datetime=origin_date_str,
                                             date_format=origin_date_format)
    return date_obj.strftime(target_date_format)


def _get_trips(search_results_obj):
    """ Get trips from the json object of search results """
    segment_obj_list = _get_segments(search_results_obj)
    trips = search_results_obj.get("trips")
    trip_obj_list = []
    for trip in trips:
        dict_trip = {
            "id": trip.get("id"),
            "departure_date": trip.get("departure_date"),
            "departure_station_id": trip.get("departure_station_id"),
            "arrival_date": trip.get("arrival_date"),
            "arrival_station_id": trip.get("arrival_station_id"),
            "price": float(trip.get("cents"))/100,
            "currency": trip.get("currency"),
            "segment_ids": trip.get("segment_ids"),
        }
        segments = []
        for segment_id in dict_trip["segment_ids"]:
            segment_found = _get_segment_from_id(
                segment_obj_list=segment_obj_list,
                segment_id=segment_id)
            if segment_found:
                segments.append(segment_found)
            else:
                dict_trip["segment_ids"].remove(segment_id)
        dict_trip["segments"] = segments

        trip_obj = Trip(dict_trip)
        trip_obj_list.append(trip_obj)
    return trip_obj_list


def _get_segments(search_results_obj):
    """ Get segments from the json object of search results """
    segments = search_results_obj.get("segments")
    segment_obj_list = []
    for segment in segments:
        dict_segment = {
            "id": segment.get("id"),
            "departure_date": segment.get("departure_date"),
            "departure_station_id": segment.get("departure_station_id"),
            "arrival_date": segment.get("arrival_date"),
            "arrival_station_id": segment.get("arrival_station_id"),
            "transportation_mean": segment.get("transportation_mean"),
            "carrier": segment.get("carrier"),
            "train_number": segment.get("train_number"),
            "travel_class": segment.get("travel_class"),
            "trip_id": segment.get("trip_id"),
            "comfort_class_ids": segment.get("comfort_class_ids"),
        }
        try:
            segment_obj = Segment(dict_segment)
            segment_obj_list.append(segment_obj)
        except TypeError:
            pass
            # Do not add a segment if it is not contain all the required fields
    return segment_obj_list


def _get_segment_from_id(segment_obj_list, segment_id):
    """ Get a segment from a list, based on a segment id """
    found_segment_obj = None
    for segment_obj in segment_obj_list:
        if segment_obj.id == segment_id:
            found_segment_obj = segment_obj
            break
    return found_segment_obj


def _filter_trips(trip_list, from_date_obj=None, to_date_obj=None,
                  min_price=0.1, max_price=None, transportation_mean=None,
                  min_segment_nb=1, max_segment_nb=None):
    """ Filter a list of trips, based on different attributes, such as
    from_date or min_price. Returns the filtered list """
    filtered_trip_list = []
    for trip in trip_list:
        to_be_filtered = False

        # Price
        if trip.price < min_price:
            to_be_filtered = True
        if max_price:
            if trip.price > max_price:
                to_be_filtered = True

        # Date
        if from_date_obj:
            if trip.departure_date_obj < from_date_obj:
                to_be_filtered = True
        if to_date_obj:
            if trip.departure_date_obj > to_date_obj:
                to_be_filtered = True

        # Transportation mean
        if transportation_mean:
            for segment in trip.segments:
                if segment.transportation_mean != transportation_mean:
                    to_be_filtered = True
                    break

        # Number of segments
        if min_segment_nb:
            if len(trip.segments) < min_segment_nb:
                to_be_filtered = True
        if max_segment_nb:
            if len(trip.segments) > max_segment_nb:
                to_be_filtered = True

        # Add to list if it has not been filtered
        if not to_be_filtered:
            filtered_trip_list.append(trip)
    return filtered_trip_list
