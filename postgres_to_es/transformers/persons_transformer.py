from typing import List

from transformers.base_transformer import BaseTransformer


class PersonTransformer(BaseTransformer):
    def transform_data(self) -> List[dict]:
        transformed_persons: List[dict] = []

        for person in self.extracted_data:
            transformed_person = {
                "_id": str(person.uuid),
                "uuid": person.uuid,
                "full_name": person.full_name,
                "birth_date": person.birth_date,
            }
            transformed_persons.append(transformed_person)

        return transformed_persons
