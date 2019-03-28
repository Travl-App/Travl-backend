from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from mainapp.models import Category, Travler


class RestCategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category

    def test_func(self):
        return self.request.user.is_superuser


class RestCategoryListView(ListView):
    model = Category

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RestCategoryListView, self).get_context_data(**kwargs)

        username = self.request.GET.get('user', 'travl')
        try:
            assert Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'user does not exist',
                'context': {'username': username},
            }

        data = {
            'status': 200,
            'user': username,
        }
        categories = context.get('category_list')
        print(categories)
        data['categories'] = [category.serialize(username, detailed=False) for category in categories.all()]

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class RestCategoryDetailView(DetailView):
    model = Category
    query_pk_or_slug = True

    def get_context_data(self, *, object_list=None, **kwargs):
        username = self.request.GET.get('user', 'travl')
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
        category = Category.objects.get(pk=uin)
        data['category'] = category.serialize(username, detailed=True)

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class RestCategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category

    def test_func(self):
        return self.request.user.is_superuser


class RestCategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category

    def test_func(self):
        return self.request.user.is_superuser
