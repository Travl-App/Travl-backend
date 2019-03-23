from datetime import datetime
from os import path

from django.conf import settings


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.record_headers(request)

        response = self.get_response(request)

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT'
        # response['Content-Type'] = 'application/json'
        # response['Accept'] = 'application/json'

        return response

    @staticmethod
    def record_headers(request):
        filepath = path.join(settings.BASE_DIR, 'headers.log')
        try:
            with open(filepath, 'a') as fp:
                fp.write(str(datetime.now()))
        except IOError:
            with open(filepath, 'w') as fp:
                fp.write(str(datetime.now()))
        try:
            with open(filepath, 'a') as fp:
                fp.write(str(request.META) + '\n\n')
        except IOError:
            print('IOError: could not open %s' % filepath)
