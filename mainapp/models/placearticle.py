from django.db import models

from mainapp.models.article import Article
from mainapp.models.place import Place, PlaceImage


class PlaceArticle(models.Model):
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ForeignKey(PlaceImage, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.IntegerField(default=0)
    description = models.TextField(verbose_name='Текст в статье')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
