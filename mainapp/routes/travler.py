from django.urls import path

from mainapp.views.travler import (
    RestTravlerCreateView, RestTravlerListView, RestTravlerDetailView,
    RestTravlerUpdateView, RestTravlerDeleteView
)

app_name = 'api_user'


urlpatterns = [
    path('create/', RestTravlerCreateView.as_view(), name='create'),  # create
    path('', RestTravlerListView.as_view(), name='list'),  # read-all (list)
    path('<slug:username>/', RestTravlerDetailView.as_view(), name='detail'),  # read
    path('<int:pk>/update', RestTravlerUpdateView.as_view(), name='update'),  # update
    path('<int:pk>/delete', RestTravlerDeleteView.as_view(), name='delete'),  # delete
]
