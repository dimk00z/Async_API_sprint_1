from transformers.base_transformer import BaseTransformer


class MoviesTransformer(BaseTransformer):
    def transform_data(self) -> list[dict]:
        transformed_movies: list[dict] = []

        for film_work in self.extracted_data:
            transformed_movie = {
                "_id": str(film_work.uuid),
                "uuid": film_work.uuid,
                "imdb_rating": film_work.rating,
                "title": film_work.title,
                "description": film_work.description,
                "genres": [
                    {"uuid": genre.uuid, "name": genre.name}
                    for genre in film_work.genres
                ],
            }

            for persons in ("writers", "actors", "directors"):
                if getattr(film_work, persons):
                    transformed_movie[persons] = [
                        {"uuid": person.uuid, "full_name": person.full_name}
                        for person in getattr(film_work, persons)
                    ]
            transformed_movies.append(transformed_movie)

        return transformed_movies
