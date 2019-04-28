from json import loads, dumps

from django.core.management import BaseCommand

from mainapp.models import Place


class Command(BaseCommand):
    help = 'Moves places\' title from JSON'

    def handle(self, *args, **options):
        sql_query = "SELECT * FROM mainapp_place"

        total = Place.objects.count()
        amended = 0
        existed = 0
        skipped = 0

        for place in Place.objects.raw(sql_query):
            print(place.id, place.title)
            # data = place.info
            # place.info = dumps(data)
            # place.save()
            data = loads(place.info)
            title = data.get('title', None)
            if title and place.title == 'noname':
                place.title = title
                data.pop('title')
                place.info = dumps(data)
                place.save()
                amended += 1
            elif place.title != 'noname':
                existed += 1
            else:
                skipped += 1
        print('Total: %s; amended: %s, existed: %s, skipped: %s; Control: %s' % (
            total, amended, existed, skipped, amended+existed+skipped
        ))
