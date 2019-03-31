from json import dumps
from os import path
from requests import get as requests_get

from django.conf import settings


def get_mapbox_data(latitude, longitude):
    url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/%(lon)s,%(lat)s.json?' % {
        'lon': float(longitude),
        'lat': float(latitude),
    }
    params = {
        'access_token': settings.MAPBOX_TOKEN,
        'types': 'place,region,country',
        'language': 'ru',
        'languageMode': 'strict',
    }
    r = requests_get(url, params)
    return r.json()


def write_mapbox_data(data):
    with open(path.join(settings.BASE_DIR, 'mapbox.json'), 'w') as fp:
        fp.write(dumps(data))


def read_mapbox_data(data):
    features = data.get('features', '')
    point, region, country = 'Не найден', 'Не найден', 'Не найден'
    if len(features):
        for feature in features:
            if len(feature.get('place_type', '')):
                if feature['place_type'][0] == 'place':
                    point = feature.get('text')
                if feature['place_type'][0] == 'region':
                    region = feature.get('text')
                if feature['place_type'][0] == 'country':
                    country = feature.get('text')
    return point, region, country
