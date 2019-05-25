from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from mainapp.models import Article, Travler
from mainapp.scripts.paginator import Paginator


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

        username = self.request.GET.get('user', 'travl')
        travlzine = self.request.GET.get('travlzine', False)
        try:
            assert Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
                'context': {'username': username},
            }

        data = {
            'status': 200,
            'user': username,
        }

        articles = context.get('article_list')

        # Pagination
        def string_names(): pass
        string_names.article_page_num = 'article_page_num'
        string_names.articles_per_page = 'articles_per_page'

        article_page_num = int(self.request.GET.get(string_names.article_page_num, '1'))
        articles_per_page = int(self.request.GET.get(string_names.articles_per_page, '11'))

        if travlzine == 'true':
            article_paginator = Paginator(
                current_page=article_page_num,
                query=articles.filter(is_chosen=True),
                items_per_page=articles_per_page)
        else:
            article_paginator = Paginator(
                current_page=article_page_num,
                query=articles,
                items_per_page=articles_per_page
            )

        if not article_paginator.page:
            return {
                'status': 404,
                'description': 'No data to show',
                'context': {
                    string_names.article_page_num: article_page_num,
                    string_names.articles_per_page: articles_per_page,
                    'paginator_count': article_paginator.count,
                    'paginator_pages': article_paginator.pages,
                }
            }
        data['count'] = article_paginator.count
        if travlzine == 'true':
            data['articles'] = [article.serialize(username, detailed=False) for article in article_paginator.page]
        else:
            data['articles'] = [article.serialize(username, detailed=True) for article in article_paginator.page]

        articles_url = '%(url)s?%(page_num_str)s=%(page_num)s&%(per_page_str)s=%(articles_number)s'
        url_data = {
            'url': reverse_lazy('api_article:list'),
            'page_num_str': string_names.article_page_num,
            'per_page_str': string_names.articles_per_page,
            'articles_number': articles_per_page,
        }


        if article_paginator.has_next():
            url_data.update({
                'page_num': article_paginator.next,
            })
            data['next'] = articles_url % url_data
        if article_paginator.has_prev():
            url_data.update({
                'page_num': article_paginator.prev,
            })
            data['prev'] = articles_url % url_data

        # if travlzine == 'true':
        #     data['articles'] = [
        #         article.serialize(username, detailed=True) for article in articles.filter(is_chosen=True)
        #     ]
        # else:
        #     data['articles'] = [article.serialize(username, detailed=False) for article in articles.all()]
        # data['count'] = len(data['articles'])
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

        username = self.request.GET.get('user', 'travl')
        uin = self.kwargs.get('pk')
        try:
            assert Travler.objects.get(username=username)
        except ObjectDoesNotExist:
            return {
                'status': 404,
                'description': 'User does not exist',
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
