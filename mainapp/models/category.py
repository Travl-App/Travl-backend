from django.db import models
from django.urls import reverse_lazy


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
