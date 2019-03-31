from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from mainapp.models import City, Travler


class RestCityCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = City

    def test_func(self):
        return self.request.user.is_superuser


class RestCityListView(ListView):
    model = City
    query_pk_or_slug = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RestCityListView, self).get_context_data(**kwargs)


        username = self.request.GET.get('user', 'travl')
        try:
            assert Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
                'context': {'username': username},
            }

        # detailed_cities = self.request.GET.get('detailed', '0')
        # detailed_cities = int(detailed_cities) if detailed_cities.isnumeric() else 0

        data = {
            'status': 200,
            'user': username,
        }
        cities = context.get('city_list')
        print(cities)
        data['cities'] = [city.serialize(username, detailed=False) for city in cities.all()]
        data['count'] = len(data['cities'])
        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class RestCityDetailView(DetailView):
    model = City
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
        city = City.objects.get(pk=uin)
        data['city'] = city.serialize(username, detailed=True)

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class RestCityUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = City

    def test_func(self):
        return self.request.user.is_superuser


class RestCityDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = City

    def test_func(self):
        return self.request.user.is_superuser
