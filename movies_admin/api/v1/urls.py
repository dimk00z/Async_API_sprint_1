from api.v1.views import MoviesDetailApi, MoviesList
from django.urls import path

urlpatterns = [
    path("movies/", MoviesList.as_view()),
    path("movies/<uuid:id>/", MoviesDetailApi.as_view()),
]
