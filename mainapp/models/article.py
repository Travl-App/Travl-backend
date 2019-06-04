from django.db import models
from django.urls import reverse_lazy

from mainapp.models import Travler


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

    def serialize(self, username, detailed=True, extended=False):
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
        for _ in self.placearticle_set.all().order_by('order'):
            # TODO: move place_article serialization in PlaceArticle model
            temp_place = {
                'id': _.place.id,
                'link': reverse_lazy('api_place:detail', kwargs={'pk': _.place.id}),
                'modified': _.place.modified.strftime('%Y-%m-%d %T %Z'),
                'title': _.place.title,
            }
            if _.image:
                temp_place['selected_image'] = _.image.image.url
            if _.image:
                if _.place.placeimage_set.exclude(pk=_.image.pk):
                    temp_place['other_images'] = [
                        image.image.url for image in _.place.placeimage_set.exclude(pk=_.image.pk)]
            if _.description:
                temp_place['article_text'] = _.description
            if _.order:
                temp_place['order'] = _.order
            result['article_places'].append(temp_place)

        categories = [_.category.serialize(username, detailed=False) for _ in self.articlecategory_set.all()]
        if len(categories):
            result['categories'] = categories

        if extended:   # minimal info about articles, but a little bit extended
            res = {
                'id': self.id,
                'title': self.title,
                'modified': self.modified.strftime('%Y-%m-%d %T %Z'),
                'link': reverse_lazy('api_article:detail', kwargs={'pk': self.id})
            }
            if result.get('image_cover'):
                res['image_cover'] = result['image_cover']
            if result.get('categories'):
                res['categories'] = result['categories']
            return res

        return result
