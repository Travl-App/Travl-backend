from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


router = [
    path('userdata/', include('mainapp.routes.travler', namespace='rest_user')),
    path('places/', include('mainapp.routes.place', namespace='rest_place')),
    path('articles/', include('mainapp.routes.article', namespace='rest_article')),
    path('categories/', include('mainapp.routes.category', namespace='rest_category')),
    path('cities/', include('mainapp.routes.city', namespace='rest_city')),
    path('map/', include('mainapp.routes.mapapi', namespace='rest_map')),
    path('query/', include('mainapp.routes.query', namespace='rest_query')),

]


urlpatterns = [
    # admin
    path('kmedtv/', admin.site.urls),
    # api
    # path('api/users/<slug:user>/', include(router)),
    path('api/', include(router)),
    # web
    path('', include('webapp.urls', namespace='web')),
]

if settings.IS_MEDIA_LOCAL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
