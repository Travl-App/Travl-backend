from django.urls import path, re_path


from webapp.views import index_view, article_view

app_name = "web"


urlpatterns = [
    # path('', index_view, name='create'),  # general page
    # re_path(r'^(?!api).*$', index_view, name='article'),  # read
    path('articles/<int:key>', article_view, name='detail')
    # path('', PlaceListView.as_view(), name='list'),  # read-all (list)
    # path('<int:pk>/update', PlaceUpdateView.as_view(), name='update'),  # update
    # path('<int:pk>/delete', PlaceDeleteView.as_view(), name='delete'),  # delete
]
