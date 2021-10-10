from typing import List

from transformers.base_transformer import BaseTransformer


class GenresTransformer(BaseTransformer):
    def transform_data(self) -> List[dict]:
        transformed_genres: List[dict] = []

        for genre in self.extracted_data:
            transformed_genre = {
                "_id": str(genre.uuid),
                "uuid": genre.uuid,
                "name": genre.name,
            }

            transformed_genres.append(transformed_genre)

        return transformed_genres
