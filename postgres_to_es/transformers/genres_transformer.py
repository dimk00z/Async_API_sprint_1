from transformers.base_transformer import BaseTransformer


class GenresTransformer(BaseTransformer):
    def transform_data(self) -> list[dict]:
        transformed_genres: list[dict] = []

        for genre in self.extracted_data:
            transformed_genre = {
                "_id": str(genre.uuid),
                "uuid": genre.uuid,
                "name": genre.name,
            }

            transformed_genres.append(transformed_genre)

        return transformed_genres
