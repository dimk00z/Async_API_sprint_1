from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now


def update_movie(instance):
    instance.film_work.updated_at = now
    instance.film_work.save()


@receiver(post_save, sender="movies.GenreFilmWork")
def save_genre_film(sender, instance, **kwargs):
    update_movie(instance)


@receiver(post_save, sender="movies.PersonFilmWork")
def save_person_film(sender, instance, **kwargs):
    update_movie(instance)


@receiver(pre_delete, sender="movies.GenreFilmWork")
def delete_genre_film(sender, instance, **kwargs):
    update_movie(instance)


@receiver(pre_delete, sender="movies.PersonFilmWork")
def delete_person_film(sender, instance, **kwargs):
    update_movie(instance)
