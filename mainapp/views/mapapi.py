from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView

from mainapp.models import Place, Travler
from mainapp.scripts.paginator import Paginator


class JsonMapListView(ListView):
    model = Place
    query_pk_or_slug = True

    # /api/users/<username>/map/?position=55.75,37.78&radius=5&auth=key
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(JsonMapListView, self).get_context_data(**kwargs)

        username = self.request.GET.get('user', 'travl')
        try:
            user = Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
                'context': {'username': username},
            }
        detailed_places = self.request.GET.get('detailed', '0')
        detailed_places = int(detailed_places) if detailed_places.isnumeric() else 0

        data = {
            'status': 200,
            'user': user.username
        }
        places = context.get('place_list')
        radius = float(self.request.GET.get('radius', 0))
        position = self.request.GET.get('position', '')
        coords = position.split(',')
        if len(coords) == 3:
            latitude, longitude, altitude = coords
        elif len(coords) == 2:
            latitude, longitude = coords
        elif not radius or len(coords) < 2:
            return {
                'status': 500,
                'description': 'Not enough data: radius and position required',
                'context': {'position': position, 'radius': radius}
            }
        else:
            raise IOError
        left_border = float(longitude) - radius
        right_border = float(longitude) + radius
        upper_border = float(latitude) + radius
        bottom_border = float(latitude) - radius

        def string_names(): pass
        string_names.place_page_num = 'place_page_num'
        string_names.places_per_page = 'places_per_page'

        place_page_num = int(self.request.GET.get(string_names.place_page_num, ['1'])[0])
        places_per_page = int(self.request.GET.get(string_names.places_per_page, ['10'])[0])

        place_paginator = Paginator(current_page=place_page_num, query=places
                                    .filter(latitude__gte=bottom_border)
                                    .filter(latitude__lte=upper_border)
                                    .filter(longitude__gte=left_border)
                                    .filter(longitude__lte=right_border), items_per_page=places_per_page)
        data['places'] = {'count': place_paginator.count, }
        data['places']['data'] = [place.serialize(username, detailed=True) for place in place_paginator.page]

        places_url = '%(url)s?%(place_page_num)s=%(place)s&detailed=%(detailed)s&position=%(position)s&radius=%(radius)s'
        url_data = {
            'url': reverse_lazy('api_map:list'),
            'place_page_num': string_names.place_page_num,
            'detailed': detailed_places,
            'position': position,
            'radius': radius
        }
        if place_paginator.has_next():
            url_data.update({
                'place': place_paginator.next,
            })
            data['places']['next'] = places_url % url_data
        if place_paginator.has_prev():
            url_data.update({
                'place': place_paginator.prev,
            })
            data['places']['prev'] = places_url % url_data

        # data['places'] = [
        #     _.serialize(username, detailed=bool(detailed_places)) for _ in places
        #     .filter(latitude__gte=bottom_border)
        #     .filter(latitude__lte=upper_border)
        #     .filter(longitude__gte=left_border)
        #     .filter(longitude__lte=right_border)
        # ]
        # data['count'] = len(data['places'])

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
