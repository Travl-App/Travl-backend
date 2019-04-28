from json import dumps
from os import path
from urllib import parse

from requests import get as requests_get

from django.conf import settings


class Coords2City:
    @staticmethod
    def get_mapbox_data(latitude, longitude):
        url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/%(lon)s,%(lat)s.json?' % {
            'lon': float(longitude),
            'lat': float(latitude),
        }
        params = {
            'access_token': settings.MAPBOX_TOKEN,
            'types': 'place,region,country',
            'language': 'ru,en',
            'languageMode': 'strict',
        }
        r = requests_get(url, params)
        return r.json()

    @staticmethod
    def write_mapbox_data(data):
        with open(path.join(settings.BASE_DIR, 'mapbox.json'), 'w') as fp:
            fp.write(dumps(data))

    @staticmethod
    def read_mapbox_data(data):
        features = data.get('features', '')
        point, region, country = 'Не найден', 'Не найден', 'Не найден'
        p_center, r_center, c_center = [], [], []
        if len(features):
            for feature in features:
                if len(feature.get('place_type', '')):
                    if feature['place_type'][0] == 'place':
                        point = feature.get('text')
                        p_center.extend(feature.get('center'))
                    if feature['place_type'][0] == 'region':
                        region = feature.get('text')
                        r_center.extend(feature.get('center'))
                    if feature['place_type'][0] == 'country':
                        country = feature.get('text')
                        c_center.extend(feature.get('center'))
        if p_center:
            center = p_center
        elif r_center:
            center = r_center
        else:
            center = c_center
        return point, region, country, tuple(center)


class City2Coords:
    @staticmethod
    def get_mapbox_data(name):
        url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/%(name)s.json' % {
            'name': parse.quote(name)
        }
        print(url)
        params = {
            'access_token': settings.MAPBOX_TOKEN,
            'autocomplete': 'false'
        }
        print(url)
        r = requests_get(url, params)
        return r.json()

    @staticmethod
    def write_mapbox_data(data):
        with open(path.join(settings.BASE_DIR, 'city2coords.json'), 'w') as fp:
            fp.write(dumps(data))
