from django.contrib import admin

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class PersonInLineAdmin(admin.TabularInline):
    model = PersonFilmWork
    extra = 0

    def get_queryset(self, request):
        qs = super(PersonInLineAdmin, self).get_queryset(request)
        return qs.select_related("person")


class GenreInLineAdmin(admin.TabularInline):
    model = GenreFilmWork
    extra = 0

    def get_queryset(self, request):
        qs = super(GenreInLineAdmin, self).get_queryset(request)
        return qs.select_related("genre")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "birth_date")
    fields = ("full_name", "birth_date")
    inlines = (PersonInLineAdmin,)
    search_fields = ("full_name", "birth_date")


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "creation_date", "rating")
    fields = (
        "title",
        "type",
        "description",
        "creation_date",
        "certificate",
        "file_path",
        "rating",
    )
    inlines = [
        PersonInLineAdmin,
        GenreInLineAdmin,
    ]
    search_fields = ("title", "description", "type", "genres")
