"""
naver_travel_time component
made by Jay Yoon
"""
from datetime import datetime
from datetime import timedelta
import logging
import requests
import json
import time
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

import voluptuous as vol

from homeassistant.components.sensor import DOMAIN, PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME, EVENT_HOMEASSISTANT_START, ATTR_LATITUDE,
    ATTR_LONGITUDE, CONF_MODE)
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import location
import homeassistant.util.dt as dt_util

_LOGGER = logging.getLogger(__name__)

CONF_API_KEY_ID = 'client_id'
CONF_DESTINATION = 'destination'
CONF_ORIGIN = 'origin'

DEFAULT_NAME = 'Naver Travel Time'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

ALL_LANGUAGES = ['ko', 'en', 'ja', 'zh']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY_ID): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_DESTINATION): cv.string,
    vol.Required(CONF_ORIGIN): cv.string,
    vol.Optional(CONF_NAME): cv.string,
})

TRACKABLE_DOMAINS = ['device_tracker', 'sensor', 'zone']
DATA_KEY = 'naver_travel_time'

class APIError(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message

def naver_direction_post(api_key_id, api_key, origin, destination):
    """ Request Naver Direction API servers"""
    
    base_url = 'https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving'
    path_url = '?start=' + origin + '&goal=' + destination
    option_url = '&option=trafast'
    url = base_url + path_url + option_url

    # check url for debug
    """
    with open('/config/naver_direction_origin.json','w', encoding="utf-8") as dumpfile:
        json.dump(url, dumpfile, ensure_ascii=False, indent="\t")
    """

    # headers
    headers = {
        'X-NCP-APIGW-API-KEY-ID': api_key_id,
        'X-NCP-APIGW-API-KEY': api_key
    }

    res = requests.get(url, headers=headers)
    out = res.json()
    """
    while True:
        res = requests.get(url, headers=headers)
        out = res.json()
        if 'code' in out:
            resultcode = out['code']
            message = out['message']
            if resultcode == 1:
                _LOGGER.warning('Origin and Destination is Same. Retrying.')
                time.sleep(300)
                continue
            elif resultcode == 0:
                break
            else:
                raise APIError(resultcode, message)
    """
    # result json file for debug
    """
    with open('/config/naver_direction.json','w', encoding="utf-8") as dumpfile:
        json.dump(out, dumpfile, ensure_ascii=False, indent="\t")
    """

    return out

def convert_time_to_utc(timestr):
    """Take a string like 08:00:00 and convert it to a unix timestamp."""
    combined = datetime.combine(
        dt_util.start_of_local_day(), dt_util.parse_time(timestr))
    if combined < datetime.now():
        combined = combined + timedelta(days=1)
    return dt_util.as_timestamp(combined)

def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Set up the Naver travel time platform."""
    def run_setup(event):
        """Delay the setup until Home Assistant is fully initialized.
        This allows any entities to be created already
        """
        if DATA_KEY not in hass.data:
            hass.data[DATA_KEY] = []
            hass.services.register(
                DOMAIN, 'naver_travel_sensor_update', update)

        if config.get(CONF_NAME) is None:
            name = DEFAULT_NAME
        else:
            name = config.get(CONF_NAME)

        api_key_id = config.get(CONF_API_KEY_ID)
        api_key = config.get(CONF_API_KEY)
        origin = config.get(CONF_ORIGIN)
        destination = config.get(CONF_DESTINATION)

        sensor = NaverTravelTimeSensor(
            hass, name, api_key_id, api_key, origin, destination)
        hass.data[DATA_KEY].append(sensor)

        if sensor.valid_api_connection:
            add_entities_callback([sensor])

    def update(service):
        """Update service for manual updates."""
        entity_id = service.data.get('entity_id')
        for sensor in hass.data[DATA_KEY]:
            if sensor.entity_id == entity_id:
                sensor.update(no_throttle=True)
                sensor.schedule_update_ha_state()

    # Wait until start event is sent to load this component.
    hass.bus.listen_once(EVENT_HOMEASSISTANT_START, run_setup)

class NaverTravelTimeSensor(Entity):
    """Representation of a Naver travel time sensor."""

    def __init__(self, hass, name, api_key_id, api_key, origin, destination):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unit_of_measurement = 'min'
        self._state = None
        self._api_key_id = api_key_id
        self._api_key = api_key
        self.valid_api_connection = True

        # Check if location is a trackable entity
        if origin.split('.', 1)[0] in TRACKABLE_DOMAINS:
            self._origin_entity_id = origin
        else:
            self._origin = origin

        if destination.split('.', 1)[0] in TRACKABLE_DOMAINS:
            self._destination_entity_id = destination
        else:
            self._destination = destination

        self.update()


    @property
    def state(self):
        """Return the state of the sensor."""
        if self._state is None:
            return None

        _data = self._state['route']['trafast'][0]['summary']
        if 'duration' in _data:
            return round((_data['duration']/1000/60), 1)
        
        return None

    @property
    def name(self):
        """Get the name of the sensor."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self._state is None:
            return None
        _data = self._state['route']['trafast'][0]['summary']
        res={}
        if 'distance' in _data:
            res['distance'] = str(round((_data['distance']/1000), 1)) + 'km'
        if 'duration' in _data:
            res['duration'] = str(round((_data['duration']/1000/60), 1)) + 'min'
        return res

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return self._unit_of_measurement

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Naver."""
        # Convert device_trackers to location
        if hasattr(self, '_origin_entity_id'):
            self._origin = self._get_location_from_entity(
                self._origin_entity_id
            )

        if hasattr(self, '_destination_entity_id'):
            self._destination = self._get_location_from_entity(
                self._destination_entity_id
            )

        self._destination = self._resolve_zone(self._destination)
        self._origin = self._resolve_zone(self._origin)

        if self._destination is not None and self._origin is not None:
            while True:
                self._state = naver_direction_post(
                    self._api_key_id, self._api_key, self._origin, self._destination)
                if 'code' in self._state:
                    resultcode = self._state['code']
                    message = self._state['message']
                    if resultcode == 1:
                        _LOGGER.warning('Origin and Destination is Same. Retrying.')
                        time.sleep(300)
                        continue
                    elif resultcode == 0:
                        break
                    else:
                        raise APIError(resultcode, message)

    def _get_location_from_entity(self, entity_id):
        """Get the location from the entity state or attributes."""
        entity = self._hass.states.get(entity_id)

        if entity is None:
            _LOGGER.error("Unable to find entity %s", entity_id)
            self.valid_api_connection = False
            return None

        # Check if the entity has location attributes
        if location.has_location(entity):
            return self._get_location_from_attributes(entity)

        # Check if device is in a zone
        zone_entity = self._hass.states.get("zone.%s" % entity.state)
        if location.has_location(zone_entity):
            _LOGGER.debug(
                "%s is in %s, getting zone location",
                entity_id, zone_entity.entity_id
            )
            return self._get_location_from_attributes(zone_entity)

        # If zone was not found in state then use the state as the location
        if entity_id.startswith("sensor."):
            return entity.state

        # When everything fails just return nothing
        return None

    @staticmethod
    def _get_location_from_attributes(entity):
        """Get the lat/long string from an entities attributes."""
        attr = entity.attributes
        location_list = [str(attr.get(ATTR_LONGITUDE)), str(attr.get(ATTR_LATITUDE))]
        return ','.join(location_list)

    def _resolve_zone(self, friendly_name):
        entities = self._hass.states.all()
        for entity in entities:
            if entity.domain == 'zone' and entity.name == friendly_name:
                return self._get_location_from_attributes(entity)

        return friendly_name
