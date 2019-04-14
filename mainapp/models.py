from json import loads

from django.db import models
from django.contrib.auth.models import AbstractUser, UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.urls import reverse_lazy


class Paginator:
    def __init__(self, current_page, model=None, items=None, query=None, items_per_page=10):
        self.current_page = current_page
        self.items_per_page = items_per_page
        self.query = query
        self.item_list = items
        self.model = model

    @property
    def count(self):
        if self.query:
            return self.query.count()
        elif self.item_list:
            return len(self.item_list)
        elif self.model:
            return self.model.objects.count()
        else:
            return 0

    @property
    def pages(self):
        return (self.count // self.items_per_page) + 1

# places_count = self.place_set.count()
# place_page_num = 10
# place_pages = places_count // place_page_num
# places_next = None
# places_prev = None

# if places_count > place_page_num:
#     place_amount = page_place * place_page_num
#     print(place_amount-10, place_amount)
#     places = list(self.place_set.all().order_by('id')[place_amount - 10:place_amount])
#     if page_place == 1 and place_pages + 1:
#         places_next = 2
#     elif page_place == place_pages + 1:
#         places_prev = place_pages
#     else:
#         places_next = page_place + 1
#         places_prev = page_place - 1
# else:
#     places = list(self.place_set.all())
# result['places'] = {'count': places_count, }

    def has_next(self):
        if self.pages > 1:
            if self.current_page < self.pages:
                return True
        return False

    @property
    def next(self):
        if self.has_next() and 0 < self.current_page < self.pages + 1:
            return self.current_page + 1
        return None

    def has_prev(self):
        if self.pages > 1:
            if self.current_page > 1:
                return True
        return False

    @property
    def prev(self):
        if self.has_prev() and 0 < self.current_page < self.pages + 1:
            return self.current_page - 1

    @property
    def page(self):
        index = self.current_page * self.items_per_page
        if self.query:
            return self.query.order_by('id')[index - self.items_per_page:index]
        if self.item_list:
            return self.item_list[index-self.items_per_page:index]
        if self.model:
            return self.model.objects.order_by('id')[index - self.items_per_page:index]


class Travler(AbstractUser):
    avatar = models.ImageField(verbose_name='Аватар', upload_to='user_avatars', blank=True, null=True)
    username_validator = UnicodeUsernameValidator()
    username = models.SlugField(_('username'),
                                unique=True, validators=[username_validator],
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
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s)" % (self.locality, self.region, )

    def serialize(self, username, detailed=True, page_place=1, page_article=1):
        result = {
            'id': self.id,
            'title': ', '.join([self.locality, self.region]),
            'country': self.country,
            'region': self.region,
            'area': self.locality,
            'modified': self.modified,
            'link': reverse_lazy('api_city:detail', kwargs={'pk': self.id})
        }
        if not detailed:
            return result
        # result['place'] = self.locality
        # result['region'] = self.region
        # result['country'] = self.country

        print('place:', page_place, 'article:', page_article)

        place_paginator = Paginator(current_page=page_place, query=self.place_set, items_per_page=10)
        result['places'] = {'count': place_paginator.count, }
        result['places']['data'] = [place.serialize(username, detailed=True) for place in place_paginator.page]
        if place_paginator.has_next():
            result['places']['next'] = '%(url)s?page_place=%(place)s&page_article=%(article)s' % {
                'url': reverse_lazy('api_city:detail', kwargs={'pk': self.id}),
                'place': place_paginator.next,
                'article': page_article
            }
        if place_paginator.has_prev():
            result['places']['prev'] = '%(url)s?page_place=%(place)s&page_article=%(article)s' % {
                'url': reverse_lazy('api_city:detail', kwargs={'pk': self.id}),
                'place': place_paginator.prev,
                'article': page_article
            }
        # places_count = self.place_set.count()
        # place_page_num = 10
        # place_pages = places_count // place_page_num
        # places_next = None
        # places_prev = None
        # if places_count > place_page_num:
        #     place_amount = page_place * place_page_num
        #     print(place_amount-10, place_amount)
        #     places = list(self.place_set.all().order_by('id')[place_amount - 10:place_amount])
        #     if page_place == 1 and place_pages + 1:
        #         places_next = 2
        #     elif page_place == place_pages + 1:
        #         places_prev = place_pages
        #     else:
        #         places_next = page_place + 1
        #         places_prev = page_place - 1
        # else:
        #     places = list(self.place_set.all())
        # result['places'] = {'count': places_count, }
        # result['places']['data'] = [place.serialize(username, detailed=True) for place in places]
        # if places_next:
        #     result['places']['next'] = f'' \
        #         f'{reverse_lazy("api_city:detail", kwargs={"pk": self.id})}' \
        #         f'?page_place={places_next}&page_article={page_article}'
        # if places_prev:
        #     result['places']['prev'] = f'' \
        #         f'{reverse_lazy("api_city:detail", kwargs={"pk": self.id})}' \
        #         f'?page_place={places_prev}&page_article={page_article}'
        all_articles = {
            article.article.pk:
                article.article.serialize(username, detailed=True)
                for place in list(place_paginator.query.all())
                for article in place.placearticle_set.all()
        }
        print(all_articles, type(all_articles))
        result['articles'] = [all_articles[key] for key in all_articles.keys()]

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
    title = models.TextField()
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

        json_data = loads(self.info)
        json_keys = ['title', 'subtitle', 'description', 'address', 'route', 'traffic', ]
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
