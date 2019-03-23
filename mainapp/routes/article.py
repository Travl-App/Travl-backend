from django.urls import path

from mainapp.views.article import (
    JsonArticleCreateView, JsonArticleListView, JsonArticleDetailView,
    JsonArticleUpdateView, JsonArticleDeleteView
)

app_name = 'api_article'


urlpatterns = [
    path('create/', JsonArticleCreateView.as_view(), name='create'),  # create
    path('', JsonArticleListView.as_view(), name='list'),  # read-all (list)
    path('<int:pk>/', JsonArticleDetailView.as_view(), name='detail'),  # read
    path('<int:pk>/update', JsonArticleUpdateView.as_view(), name='update'),  # update
    path('<int:pk>/delete', JsonArticleDeleteView.as_view(), name='delete'),  # delete
]
