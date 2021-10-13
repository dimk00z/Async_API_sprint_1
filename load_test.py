import random
from locust import HttpUser, between, task

# to run:
# `pip install locust && locust -f load_test.py`

with open("main_film_work.csv") as f_in:
    film_works = list(map(lambda x: x.strip(), f_in.readlines()))

with open("main_genre.csv") as f_in:
    genres = list(map(lambda x: x.strip(), f_in.readlines()))

with open("main_person.csv") as f_in:
    persons = list(map(lambda x: x.strip(), f_in.readlines()))


class WebsiteUser(HttpUser):
    wait_time = between(0.1, 3)

    @task
    def film_info(self):
        self.client.get(f"/api/v1/film/{random.choice(film_works)}")

    @task
    def person_info(self):
        self.client.get(f"/api/v1/person/{random.choice(persons)}")

    @task
    def genre_info(self):
        self.client.get(f"/api/v1/genre/{random.choice(genres)}")
