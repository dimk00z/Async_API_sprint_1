from typing import List
from uuid import UUID

from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Page, Paginator
from django.db.models import Model, Q
from django.db.models.query import QuerySet
from django.http import Http404, JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import FilmWork


class MoviesApiMixin:
    model: Model = FilmWork
    http_method_names: List[str] = ["get"]

    def aggregate_person(self, role) -> ArrayAgg:
        return ArrayAgg(
            "persons__person__full_name",
            filter=Q(persons__role__exact=role),
            distinct=True,
        )

    def get_queryset(self):
        films: QuerySet = (
            FilmWork.objects.prefetch_related("persons", "film_genres")
            .values()
            .annotate(
                genres=ArrayAgg("film_genres__genre__name", distinct=True),
                actors=self.aggregate_person(role="actor"),
                directors=self.aggregate_person(role="director"),
                writers=self.aggregate_person(role="writer"),
            )
        )
        return films

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, json_dumps_params={"indent": " "}, safe=False)


class MoviesList(MoviesApiMixin, BaseListView):
    paginate_by: int = 50
    ordering: str = "title"

    def get_context_data(self, *, object_list=None, **kwargs):
        context: dict = super().get_context_data()

        paginator: Paginator = context["paginator"]
        page: Page = context["page_obj"]
        paginated_films: QuerySet = context["page_obj"]
        result: dict = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(paginated_films),
        }
        return result


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        return super().get_context_data().get("object")
