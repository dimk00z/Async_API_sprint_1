from typing import List


class Transformer:
    def __init__(self, extracted_movies: dict) -> None:
        self.extracted_movies = extracted_movies

    def transform_movies(self) -> List[dict]:
        transformed_movies: List[dict] = []

        for film_work in self.extracted_movies:
            transformed_movie = {
                "_id": film_work.id,
                "imdb_rating": film_work.rating,
                "title": film_work.title,
                "description": film_work.description,
                "genres": [genre for genre in film_work.genres],
            }
            for persons in ("writers", "actors", "directors"):
                if getattr(film_work, persons):
                    transformed_movie[persons] = [
                        {"id": person.id, "name": person.full_name} for person in getattr(film_work, persons)
                    ]
                    if persons != "directors":
                        transformed_movie[f"{persons}_names"] = [
                            person.full_name for person in getattr(film_work, persons)
                        ]
            transformed_movies.append(transformed_movie)

        return transformed_movies
