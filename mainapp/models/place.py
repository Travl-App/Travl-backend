from json import loads

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse_lazy

from mainapp.models import Travler
from mainapp.models.city import City


class Place(models.Model):
    travler = models.ForeignKey(Travler, on_delete=models.CASCADE)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.TextField(max_length=50)
    info = JSONField()
    latitude = models.DecimalField(verbose_name="Широта", max_digits=10, decimal_places=7)
    longitude = models.DecimalField(verbose_name="Долгота", max_digits=10, decimal_places=7)
    altitude = models.IntegerField(verbose_name="Высота")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.title:
            title = "%s..." % self.title[:47] if len(self.title) > 46 else self.title
        else:
            title = 'No title'
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

        if isinstance(self.info, dict):
            json_data = self.info
        else:
            json_data = loads(self.info)
        json_keys = ['subtitle', 'description', 'address', 'route', 'traffic', 'www', ]
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
