from os import listdir, path
from json import dumps, loads
from random import shuffle as random_shuffle, choice as random_choice
from time import sleep

from requests import get as requests_get
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings

from mainapp.models import (
    Travler, City,
    Article, ArticleCategory, Category,
    Place, PlaceImage, PlaceCategory, PlaceArticle
)
from mainapp.scripts.geocode import Coords2City


with open(path.join(settings.BASE_DIR, 'raw_data.json'), 'r') as fp:
    raw_places = loads(fp.read())


def get_random_text(amount=1):
    r = requests_get('https://baconipsum.com/api/?type=all-meat&paras=%s' % amount)
    return list(r.json())


def walker(my_path='.', extension=None):
    if extension:
        return [f for f in listdir(my_path) if f.split('.')[-1] in extension]
    else:
        return [f for f in listdir(my_path)]
    pass


class CreateObjects:
    def __init__(self, username='travl'):
        self.user = Travler.objects.get(username=username)
        self.images_dir = path.join(settings.BASE_DIR, 'sources', 'images')
        self.filenames = walker(self.images_dir)
        self.category_names = [
            'Архитектура',
            'Вид',
            'Urbex',
            'Музей',
            'Природа',
            'Место для прогулок',
            'Покупки',
            'Еда',
            'Отель',
            'Странное',
            'Находка',
        ]

    def places(self):
        print("Generate places")
        places = []
        for item in raw_places:
            place = Place()
            place.latitude = item['latitude']
            place.longitude = item['longitude']
            place.altitude = 0
            place.travler = self.user
            place.info = dumps({
                'title': item['title'],
                'description': item['description']
            })
            places.append(place)
        Place.objects.bulk_create(places)
        print("Added %s places, now there are %s places" % (len(places), Place.objects.count()))

    def cities(self):
        assert self
        places = Place.objects.filter(city=None)
        counter = 0
        limit = len(places)
        print('There are %s places without city information' % limit)
        for place in places:
            data = Coords2City.get_mapbox_data(latitude=place.latitude, longitude=place.longitude)
            Coords2City.write_mapbox_data(data=data)
            point, region, country, center = Coords2City.read_mapbox_data(data=data)
            counter += 1
            print(counter, place.id, point, region, country, center)
            try:
                city = City.objects.get(locality=point, region=region, country=country)
            except ObjectDoesNotExist:
                city = City()
                city.locality = point
                city.region = region
                city.country = country
                if center:
                    city.latitude = center[1]
                    city.longitude = center[0]
                city.save()
            place.city = city
            place.save()
            sleep(random_choice(range(3, 6)))

    def categories(self):
        assert self.user
        print("Generated categories")
        categories = []
        for name in self.category_names:
            category = Category()
            category.name = 'Категория %s' % name
            categories.append(category)
        Category.objects.bulk_create(categories)
        print("Added %s categories, now there are %s categories" % (len(categories), Category.objects.count()))

    def place_category(self):
        assert self.user
        print("Generating random place-category connections")
        places_categories = []
        places = list(Place.objects.all())
        categories = list(Category.objects.all())
        random_shuffle(places)
        for place in places[:-10]:
            cat_nums = list(set([
                random_choice(list(range(0, len(categories)))) for _ in range(1, random_choice(range(1, 3)))
            ]))
            for cat_num in cat_nums:
                connection = PlaceCategory()
                connection.place = place
                connection.category = categories[cat_num]
                places_categories.append(connection)
        PlaceCategory.objects.bulk_create(places_categories)
        print("Added %s place-categories, now there are %s place-categories" % (
            len(places_categories), PlaceCategory.objects.count()))

    def articles(self):
        print("Generating random articles")
        for i in range(10):
            text = get_random_text(3)
            article = Article()
            article.travler = self.user
            article.title = ' '.join(text[0].split(' ')[:random_choice([3, 4, 5, 6])])  # TODO
            if random_choice((0, 1)):
                article.subtitle = text[1][:50]  # TODO
            article.description = text[2]  # TODO
            filename = self.filenames.pop()
            article.image_cover.save(filename, File(open(path.join(self.images_dir, filename), 'rb')))
        print("Generated %s articles" % Article.objects.count())

    def place_image(self):
        print("Generating mandatory one place-image connection")
        places = Place.objects.all()
        for place in places:
            filename = self.filenames.pop()
            image = PlaceImage()
            image.place = place
            image.image.save(filename, File(open(path.join(self.images_dir, filename), 'rb')))
        print("Generated %s place-image connections" % (PlaceImage.objects.count(), ))
        print("Generating random place-image connections")
        counter = 0
        for filename in self.filenames:
            image = PlaceImage()
            image.place = random_choice(places)
            image.image.save(filename, File(open(path.join(self.images_dir, filename), 'rb')))
            counter += 1
        print("Generated %s random place-image connections" % counter)
        print("Generated %s place-image connections in total" % PlaceImage.objects.count())

    def place_article(self):
        assert self.user
        print("Generating random place-article connections")
        place_articles = []
        articles = Article.objects.all()
        places = list(Place.objects.all())
        place_descriptions = []
        for article in articles:
            random_shuffle(places)
            order = 0
            for place in places[:random_choice(list(range(4, 10)))]:
                place_article = PlaceArticle()
                place_article.place = place
                place_article.article = article
                order += 1
                place_article.order = order
                place_article.image = random_choice(list(place.placeimage_set.all()))
                place_descriptions = place_descriptions if len(place_descriptions) else get_random_text(10)
                place_article.description = place_descriptions.pop()
                place_articles.append(place_article)
        PlaceArticle.objects.bulk_create(place_articles)
        print("Generated %s place-article connections" % PlaceArticle.objects.count())

    def article_category(self):
        assert self.user
        print("Generating random article-category connections")
        article_categories = []
        articles = Article.objects.all()
        for article in articles:
            categories = set({})
            # print(article.placearticle_set.all())
            places_articles = article.placearticle_set.all()
            places = [place.place for place in places_articles]
            for place in places:
                categories.update(place.placecategory_set.all())
            categories = set([category.category.id for category in list(categories)])
            categories = [Category.objects.get(id=pk) for pk in categories]
            # print(categories)
            for category in categories:
                article_category = ArticleCategory()
                article_category.article = article
                article_category.category = category
                article_categories.append(article_category)
        ArticleCategory.objects.bulk_create(article_categories)
        print("Generated %s article-category connections" % ArticleCategory.objects.count())


class Command(BaseCommand):
    help = 'Fill database with data'

    def add_arguments(self, parser):
        parser.add_argument('obj', nargs='?', default='all')

    def handle(self, *args, **options):
        print(options)
        cmd = options.get('obj', '')
        gen = CreateObjects()
        if cmd in ['all', 'places']:
            gen.places()
        if cmd in ['all', 'cities']:
            gen.cities()
        if cmd in ['all', 'categories']:
            gen.categories()
        if cmd in ['all', 'place_category']:
            gen.place_category()
        if cmd in ['all', 'articles']:
            gen.articles()
        if cmd in ['all', 'place_image']:
            gen.place_image()
        if cmd in ['all', 'place_article']:
            gen.place_article()
        if cmd in ['all', 'article_category']:
            gen.article_category()
