from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic import ListView

from mainapp.models import City, Travler
from mainapp.scripts.geocode import get_mapbox_data, write_mapbox_data, read_mapbox_data


class QueryListView(ListView):
    model = City
    query_pk_or_slug = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(QueryListView, self).get_context_data(**kwargs)

        username = self.request.GET.get('user', 'travl')
        try:
            assert Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
                'context': {'username': username},
            }

        position = self.request.GET.get('position', '')
        coords = position.split(',')
        if len(coords) == 3:
            latitude, longitude, altitude = coords
        elif len(coords) == 2:
            latitude, longitude = coords
        else:
            return {
                'status': 500,
                'description': 'Not enough data: position required',
                'context': {'position': position}
            }

        cities = context.get('city_list')

        data = get_mapbox_data(latitude=latitude, longitude=longitude)
        write_mapbox_data(data)
        point, region, country = read_mapbox_data(data)
        try:
            city = cities.get(locality=point, region=region, country=country)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'No entries at this location',
                'context': {
                    'latitude': latitude, 'longitude': longitude,
                    'place': point, 'region': region, 'country': country
                }
            }

        data = {
            'status': 200,
            'user': username,
            'city': city.serialize(username, detailed=True, **self.request.GET)
        }

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
