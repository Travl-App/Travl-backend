from django.urls import path

from mainapp.views.category import (
    RestCategoryCreateView, RestCategoryListView, RestCategoryDetailView,
    RestCategoryUpdateView, RestCategoryDeleteView
)

app_name = 'api_category'


urlpatterns = [
    path('create/', RestCategoryCreateView.as_view(), name='create'),  # create
    path('', RestCategoryListView.as_view(), name='list'),  # read-all (list)
    path('<int:pk>/', RestCategoryDetailView.as_view(), name='detail'),  # read
    path('<int:pk>/update', RestCategoryUpdateView.as_view(), name='update'),  # update
    path('<int:pk>/delete', RestCategoryDeleteView.as_view(), name='delete'),  # delete
]
