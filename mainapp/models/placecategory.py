from django.db import models

from mainapp.models.category import Category
from mainapp.models.place import Place


class PlaceCategory(models.Model):
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
