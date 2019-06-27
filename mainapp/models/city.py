from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse_lazy

from mainapp.scripts.paginator import Paginator


class City(models.Model):
    title = models.TextField()
    locality = models.TextField()
    region = models.TextField()
    country = models.TextField()
    bbox = JSONField()
    radius = models.DecimalField(verbose_name='Радиус', max_digits=10, decimal_places=7, null=True, blank=True)
    latitude = models.DecimalField(verbose_name="Широта", max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(verbose_name="Долгота", max_digits=10, decimal_places=7, null=True, blank=True)
    altitude = models.IntegerField(verbose_name="Высота", default=0)
    #wikidata
    image = models.ImageField(verbose_name='АватарГорода', upload_to='city_images', blank=True, null=True)
    qlink = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

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
            'title': self.title,
            'country': self.country,
            'region': self.region,
            'area': self.locality,
            'modified': self.modified,
            'link': reverse_lazy('api_city:detail', kwargs={'pk': self.id})
        }
        if self.latitude is not None and self.longitude is not None:
            result['coordinates'] = [float(self.latitude), float(self.longitude), float(self.altitude)]
        if self.radius is not None:
            result['radius'] = float(self.radius)
        if self.bbox:
            result['bbox'] = self.bbox
        if self.image:
            result['image'] = self.image.url
        if self.description:
            result['description'] = self.description
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
                article.article.serialize(username, extended=True)
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
