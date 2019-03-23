from django.views.generic import ListView, DetailView
from django.views import View
from django.http.response import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from mainapp.models import Place, Travler


class RestPlaceListView(ListView):
    model = Place
    query_pk_or_slug = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RestPlaceListView, self).get_context_data(**kwargs)

        username = self.kwargs.get('user')
        try:
            user = Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 403,
                'description': 'user does not exist',
                'context': {'username': username},
            }

        data = {
            'status': 200,
            'user': user.username
        }
        places = context.get('place_list')
        data['count'] = len(places)
        data['places'] = [_.serialize(username, detailed=False) for _ in places]

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

        username = self.kwargs.get('user')
        uin = self.kwargs.get('pk')
        try:
            user = Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 'error',
                'description': 'user does not exist',
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
