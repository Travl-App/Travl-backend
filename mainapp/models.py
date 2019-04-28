from json import loads

from django.db import models
from django.contrib.auth.models import AbstractUser, UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.urls import reverse_lazy

from mainapp.scripts.paginator import Paginator


class Travler(AbstractUser):
    avatar = models.ImageField(verbose_name='Аватар', upload_to='user_avatars', blank=True, null=True)
    username_validator = UnicodeUsernameValidator()
    username = models.SlugField(_('username'),
                                unique=True, validators=[username_validator], max_length=30,
                                error_messages={
                                    'unique': _("A user with that username already exists."),
                                },)
    info = JSONField()
    is_active = models.BooleanField(default=True)
    is_author = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "User: %s" % self.username

    def serialize(self, username, detailed=True):
        result = {
            'username': self.username,
            'modified': self.modified,
            'link': reverse_lazy('api_user:detail', kwargs={'username': self.username})
        }
        if not detailed:
            return result
        result.update({
            'is_active': self.is_active,
        })
        if self.avatar:
            result['image'] = self.avatar.url

        return result


class City(models.Model):
    locality = models.TextField()
    region = models.TextField()
    country = models.TextField()
    latitude = models.DecimalField(verbose_name="Широта", max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(verbose_name="Долгота", max_digits=10, decimal_places=8, null=True, blank=True)
    altitude = models.IntegerField(verbose_name="Высота", default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s)" % (self.locality, self.region, )

    def serialize(self, username, detailed=True, **kwargs):

        def string_names(): pass
        string_names.place_page_num = 'place_page_num'
        string_names.places_per_page = 'places_per_page'
        string_names.article_page_num = 'article_page_num'
        string_names.articles_per_page = 'articles_per_page'

        result = {
            'id': self.id,
            'title': ', '.join([self.locality, self.region]),
            'country': self.country,
            'region': self.region,
            'area': self.locality,
            'modified': self.modified,
            'link': reverse_lazy('api_city:detail', kwargs={'pk': self.id})
        }
        if self.latitude is not None and self.longitude is not None:
            result['coordinates'] = [float(self.latitude), float(self.longitude), float(self.altitude)]
        if not detailed:
            return result
        print('KWARGS:', kwargs)

        place_page_num = int(kwargs.get(string_names.place_page_num, ['1'])[0])
        places_per_page = int(kwargs.get(string_names.places_per_page, ['10'])[0])
        article_page_num = int(kwargs.get(string_names.article_page_num, ['1'])[0])
        articles_per_page = int(kwargs.get(string_names.articles_per_page, ['10'])[0])

        print(
            'place:', place_page_num, 'article:', article_page_num
        )

        place_paginator = Paginator(current_page=place_page_num, query=self.place_set, items_per_page=places_per_page)
        result['places'] = {'count': place_paginator.count, }
        result['places']['data'] = [place.serialize(username, detailed=True) for place in place_paginator.page]

        city_url = '%(url)s?%(place_page_num)s=%(place)s&%(article_page_num)s=%(article)s'
        url_data = {
            'url': reverse_lazy('api_city:detail', kwargs={'pk': self.id}),
            'place_page_num': string_names.place_page_num,
            'article_page_num': string_names.article_page_num
        }
        if place_paginator.has_next():
            url_data.update({
                'place': place_paginator.next,
                'article': article_page_num
            })
            result['places']['next'] = city_url % url_data
        if place_paginator.has_prev():
            url_data.update({
                'place': place_paginator.prev,
                'article': article_page_num
            })
            result['places']['prev'] = city_url % url_data

        all_articles = {
            article.article.pk:
                article.article.serialize(username, detailed=True)
                for place in list(place_paginator.query.all())
                for article in place.placearticle_set.all()
        }
        article_paginator = Paginator(
            current_page=article_page_num, items_per_page=articles_per_page,
            items=[all_articles[key] for key in all_articles.keys()]
        )

        result['articles'] = {'count': article_paginator.count, }
        result['articles']['data'] = article_paginator.page
        if article_paginator.has_next():
            url_data.update({
                'place': place_page_num,
                'article': article_paginator.next
            })
            result['articles']['next'] = city_url % url_data
        if article_paginator.has_prev():
            url_data.update({
                'place': place_page_num,
                'article': article_paginator.prev
            })
            result['articles']['prev'] = city_url % url_data

        return result


class Category(models.Model):
    name = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Категория: %s" % self.name

    def serialize(self, username, detailed=True):
        result = {
            'id': self.id,
            'name': self.name,
            'modified': self.modified,
            'link': reverse_lazy('api_category:detail', kwargs={'pk': self.id})
        }
        if not detailed:
            return result
        result['places'] = [place.place.serialize(username, detailed=False) for place in self.placecategory_set.all()]
        result['articles'] = [
            article.article.serialize(username, detailed=False) for article in self.articlecategory_set.all()
        ]
        return result


class Article(models.Model):
    travler = models.ForeignKey(Travler, null=True, blank=True, on_delete=models.SET_NULL)
    is_chosen = models.BooleanField(default=False)
    title = models.TextField(max_length=65)
    subtitle = models.TextField()
    image_cover = models.ImageField(verbose_name='Обложка', upload_to='article_cover', blank=True, null=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = '%s...' % self.title[:47] if len(self.title) > 46 else self.title
        return "Статья(%s): %s" % (self.pk, name,)

    def serialize(self, username, detailed=True):
        result = {
            'id': self.id,
            'title': self.title,
            'modified': self.modified.strftime('%Y-%m-%d %T %Z'),
            'link': reverse_lazy('api_article:detail', kwargs={'pk': self.id})
        }
        if not detailed:
            return result
        result['author'] = self.travler.serialize(username, detailed=True)
        result['article_places'] = []

        if self.subtitle:
            result['subtitle'] = self.subtitle
        if self.description:
            result['description'] = self.description
        if self.image_cover:
            result['image_cover'] = self.image_cover.url
        for _ in self.placearticle_set.all():
            # TODO: move place_article serialization in PlaceArticle model
            temp_place = {
                'id': _.place.id,
                'link': reverse_lazy('api_place:detail', kwargs={'pk': _.place.id}),
                'modified': _.place.modified.strftime('%Y-%m-%d %T %Z')
            }
            if _.image:
                temp_place['selected_image'] = _.image.image.url
            if _.image:
                if _.place.placeimage_set.exclude(pk=_.image.pk):
                    temp_place['other_images'] = [image.image.url for image in _.place.placeimage_set.exclude(pk=_.image.pk)]
            if _.description:
                temp_place['description'] = _.description
            if _.order:
                temp_place['order'] = _.order
            result['article_places'].append(temp_place)

        categories = [_.category.serialize(username, detailed=False) for _ in self.articlecategory_set.all()]
        if len(categories):
            result['categories'] = categories

        return result


class Place(models.Model):
    travler = models.ForeignKey(Travler, on_delete=models.CASCADE)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.TextField(max_length=50)
    info = JSONField()
    latitude = models.DecimalField(verbose_name="Широта", max_digits=10, decimal_places=8)
    longitude = models.DecimalField(verbose_name="Долгота", max_digits=10, decimal_places=8)
    altitude = models.IntegerField(verbose_name="Высота")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        title = loads(self.info).get('title')
        if title:
            title = "%s..." % title[:47] if len(title) > 46 else title
        return "М(%s): %s" % (self.pk, title, )

    def serialize(self, username, detailed=True):
        result = {
            'id': self.id,
            'modified': self.modified,
            'link': reverse_lazy('api_place:detail', kwargs={'pk': self.id}),
        }
        if not detailed:
            return result
        result['author'] = self.travler.serialize(username, detailed=True)
        result['coordinates'] = [float(self.latitude), float(self.longitude), float(self.altitude)]
        result['title'] = self.title

        json_data = loads(self.info)
        json_keys = ['subtitle', 'description', 'address', 'route', 'traffic', ]
        for key in json_keys:
            if json_data.get(key):
                result[key] = json_data.get(key)
        # images
        # 'images': None,  # ["<str:imageUrl>", "<str:imageUrl>", ...]*,
        images = [_.image.url for _ in self.placeimage_set.all()]
        if len(images):
            result['images'] = images
        # articles
        articles = [_.article.serialize(username, detailed=False) for _ in self.placearticle_set.all()]
        if len(articles):
            result['articles'] = articles
        # categories
        categories = [
            _.category.serialize(username, detailed=False) for _ in self.placecategory_set.all()
        ]
        if len(categories):
            result['categories'] = categories
        return result


class PlaceImage(models.Model):
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ImageField(verbose_name='Изображение', upload_to='place_images')
    alt = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Картинка: %s - %s" % (self.place, self.image.name)


class PlaceCategory(models.Model):
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class PlaceArticle(models.Model):
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ForeignKey(PlaceImage, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.IntegerField(default=0)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ArticleCategory(models.Model):
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
