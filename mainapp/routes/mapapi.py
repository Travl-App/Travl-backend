from django.urls import path

from mainapp.views.mapapi import JsonMapListView


app_name = "api_map"


urlpatterns = [
    # path('create/', PlaceCreateView.as_view(), name='create'),  # create
    # path('<int:pk>/', RestPlaceDetailView.as_view(), name='detail'),  # read
    path('', JsonMapListView.as_view(), name='list'),  # read-all (list)
    # path('<slug:slug>/update', PlaceUpdateView.as_view(), name='update'),  # update
    # path('<slug:slug>/delete', PlaceDeleteView.as_view(), name='delete'),  # delete
]
