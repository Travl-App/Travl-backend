from django.urls import path


from webapp.views import index_view


app_name = "web"


urlpatterns = [
    path('', index_view, name='create'),  # general page
    # path('<int:pk>/', PlaceDetailView.as_view(), name='detail'),  # read
    # path('', PlaceListView.as_view(), name='list'),  # read-all (list)
    # path('<int:pk>/update', PlaceUpdateView.as_view(), name='update'),  # update
    # path('<int:pk>/delete', PlaceDeleteView.as_view(), name='delete'),  # delete
]
