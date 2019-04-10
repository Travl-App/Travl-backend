from django.urls import path


from webapp.views import article_view, place_view

app_name = "web"


urlpatterns = [
    # path('', index_view, name='create'),  # general page
    # re_path(r'^(?!api).*$', index_view, name='article'),  # read
    path('articles/<int:key>/', article_view, name='article-detail'),
    path('places/<int:key>/', place_view, name='place-detail'),
    # path('', PlaceListView.as_view(), name='list'),  # read-all (list)
    # path('<int:pk>/update', PlaceUpdateView.as_view(), name='update'),  # update
    # path('<int:pk>/delete', PlaceDeleteView.as_view(), name='delete'),  # delete
]
