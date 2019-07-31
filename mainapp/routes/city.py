from django.urls import path

from mainapp.views.city import (
    RestCityCreateView, RestCityListView, RestCityDetailView, RestCityInfoView,
    RestCityUpdateView, RestCityDeleteView
)

app_name = 'api_city'


urlpatterns = [
    path('create/', RestCityCreateView.as_view(), name='create'),  # create
    path('', RestCityListView.as_view(), name='list'),  # read-all (list)
    path('<int:pk>/', RestCityDetailView.as_view(), name='detail'),  # read
    path('<int:pk>/info', RestCityInfoView.as_view(), name='info'),
    path('<int:pk>/update', RestCityUpdateView.as_view(), name='update'),  # update
    path('<int:pk>/delete', RestCityDeleteView.as_view(), name='delete'),  # delete
]
