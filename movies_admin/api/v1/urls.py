from django.urls import path
from api.v1.views import MoviesList, MoviesDetailApi

urlpatterns = [
    path("movies/", MoviesList.as_view()),
    path("movies/<uuid:id>/", MoviesDetailApi.as_view()),
]
