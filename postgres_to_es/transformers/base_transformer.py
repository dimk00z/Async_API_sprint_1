from typing import List


class BaseTransformer:
    def __init__(self, extracted_data: dict) -> None:
        self.extracted_data = extracted_data

    def transform_data(self) -> List[dict]:
        pass