from django.views.generic import ListView, DetailView
from django.views import View
from django.http.response import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from mainapp.models import Travler
from mainapp.models.place import Place


class RestPlaceListView(ListView):
    model = Place
    query_pk_or_slug = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RestPlaceListView, self).get_context_data(**kwargs)

        username = self.request.GET.get('user', 'travl')
        try:
            user = Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
                'context': {'username': username},
            }

        data = {
            'status': 200,
            'user': user.username
        }

        position = self.request.GET.get('position', '')
        if position:
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

            place = Place.objects.select_related('city').filter(latitude=latitude).filter(longitude=longitude).first()
            if place:
                data['place'] = place.serialize(username, detailed=True)
                return data
            else:
                return {
                    'status': 404,
                    'description': 'Could not find place with this coordinates',
                    'context': {'username': username, 'latitude': latitude, 'longitude': longitude},
                }

        places = context.get('place_list')
        data['places'] = [_.serialize(username, detailed=False) for _ in places]
        data['count'] = len(data['places'])
        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class RestPlaceDetailView(DetailView):
    model = Place
    # slug_url_kwarg = 'user'
    # pk_url_kwarg = 'place'
    query_pk_or_slug = True

    def get_context_data(self, *, object_list=None, **kwargs):
        # context = super(RestPlaceDetailView, self).get_context_data(**kwargs)

        username = self.request.GET.get('user', 'travl')
        uin = self.kwargs.get('pk')
        try:
            user = Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
                'context': {'username': username},
            }

        data = {
            'status': 200,
            'user': user.username
        }
        # TODO: why there is select_related('city')
        place = Place.objects.select_related('city').get(pk=uin)
        data['place'] = place.serialize(username, detailed=True)

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class PlaceCreateView(View):
    def post(self):
        self.request.POST.get()
        print()
        return HttpResponse('result')

    def get(self, request):
        raise Http404


class PlaceListView(View):
    pass

# user_id = models.ForeignKey(TravlUser, on_delete=models.CASCADE)
# city_id = models.ForeignKey(City, on_delete=models .SET_NULL, null=True, blank=True)
# info = JSONField()
# latitude = models.DecimalField(verbose_name="Широта", max_digits=10, decimal_places=8)
# longitude = models.DecimalField(verbose_name="Долгота", max_digits=10, decimal_places=8)
# altitude = models.IntegerField(verbose_name="Высота")
# created = models.DateTimeField(auto_now_add=True)
# modified = models.DateTimeField(auto_now=True)
