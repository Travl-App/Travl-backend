from django.urls import path

from mainapp.views.query import QueryListView

app_name = "api_query"


urlpatterns = [
    # path('create/', PlaceCreateView.as_view(), name='create'),  # create
    # path('<int:pk>/', RestPlaceDetailView.as_view(), name='detail'),  # read
    path('', QueryListView.as_view(), name='list'),  # read-all (list)
    # path('<slug:slug>/update', PlaceUpdateView.as_view(), name='update'),  # update
    # path('<slug:slug>/delete', PlaceDeleteView.as_view(), name='delete'),  # delete
]
