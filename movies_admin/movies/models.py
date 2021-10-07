import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FilmWorkType(models.TextChoices):
    MOVIE = "movie", _("movie")
    TV_SHOW = "tv_show", _("TV Show")


class RoleType(models.TextChoices):
    ACTOR = "actor", _("actor")
    WRITER = "writer", _("writer")
    DIRECTOR = "director", _("director")


class FilmWork(TimeStampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(_("title"), max_length=250)
    description = models.TextField(_("description"), blank=True, null=True)
    creation_date = models.DateField(_("creation date"), blank=True, null=True)
    certificate = models.TextField(_("certificate"), blank=True, null=True)
    file_path = models.FileField(
        _("file"), upload_to="film_works/", blank=True, null=True
    )
    rating = models.FloatField(
        _("rating"),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        blank=True,
        null=True,
    )
    type = models.CharField(
        _("type"),
        max_length=20,
        choices=FilmWorkType.choices,
        default=FilmWorkType.MOVIE,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Film")
        verbose_name_plural = _("Films")
        db_table = '"content"."film_work"'
        ordering = ["-rating"]


class Genre(TimeStampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(_("title"), unique=True, max_length=100)
    description = models.TextField(_("description"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")
        db_table = '"content"."genre"'
        ordering = ["name"]


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    film_work = models.ForeignKey(
        FilmWork,
        db_column="film_work_id",
        on_delete=models.CASCADE,
        related_name="film_genres",
    )
    genre = models.ForeignKey(
        "Genre",
        db_column="genre_id",
        related_name="film_works",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.genre.name

    class Meta:
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")
        db_table = '"content"."genre_film_work"'
        ordering = ["genre__name"]
        unique_together = ("film_work", "genre")


class Person(TimeStampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    full_name = models.CharField(_("full_name"), max_length=200)
    birth_date = models.DateField(_("birth_date"), blank=True, null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        db_table = '"content"."person"'
        ordering = ["full_name"]


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    role = models.CharField(_("role"), choices=RoleType.choices, max_length=50)
    film_work = models.ForeignKey(
        FilmWork,
        db_column="film_work_id",
        related_name="persons",
        on_delete=models.CASCADE,
    )
    person = models.ForeignKey(
        "Person",
        db_column="person_id",
        related_name="film_works",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.person.full_name} - {self.role}"

    class Meta:
        verbose_name = _("Connection Film to Person")
        verbose_name_plural = _("Connections Film to Person")
        db_table = '"content"."person_film_work"'
        unique_together = (("film_work", "person", "role"),)
        ordering = ["role"]
