from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic import ListView

from mainapp.models import Place, Travler


class JsonMapListView(ListView):
    model = Place
    query_pk_or_slug = True

    # /api/users/<username>/map/?position=55.75,37.78&radius=5&auth=key
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(JsonMapListView, self).get_context_data(**kwargs)

        username = self.kwargs.get('user')
        try:
            user = Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 403,
                'description': 'user does not exist',
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
        data['places'] = [
            _.serialize(username, detailed=bool(detailed_places)) for _ in places
            .filter(latitude__gte=bottom_border)
            .filter(latitude__lte=upper_border)
            .filter(longitude__gte=left_border)
            .filter(longitude__lte=right_border)
        ]
        data['count'] = len(data['places'])

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
