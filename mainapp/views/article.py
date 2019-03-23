from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from mainapp.models import Article, Travler


class JsonArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Article

    def test_func(self):
        return self.request.user.is_superuser


class JsonArticleListView(ListView):
    model = Article
    query_pk_or_slug = True

    # /api/users/<username>/places?position=55.75,37.78&radius=5&auth=key
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(JsonArticleListView, self).get_context_data(**kwargs)

        username = self.kwargs.get('user')
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
        articles = context.get('article_list')
        print(articles)
        data['articles'] = [article.serialize(username, detailed=False) for article in articles.all()]

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)

    def test_func(self):
        return self.request.user.is_superuser


class JsonArticleDetailView(DetailView):
    model = Article
    query_pk_or_slug = True

    def get_context_data(self, *, object_list=None, **kwargs):
        # context = super(RestPlaceDetailView, self).get_context_data(**kwargs)

        username = self.kwargs.get('user')
        uin = self.kwargs.get('pk')
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
            'user': username
        }
        article = Article.objects.get(pk=uin)
        data['article'] = article.serialize(username=username)

        return data

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class JsonArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article

    def test_func(self):
        return self.request.user.is_superuser


class JsonArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article

    def test_func(self):
        return self.request.user.is_superuser
