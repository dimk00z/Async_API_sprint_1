# Решение 3 проектного задания второго спринта

1. Проинициализирован проект Django `python manage.py startproject config .`
2. Перенесены настройки в `config\settings`  с разделением на настройки `dev.py` и `production.py`
3. Настройки БД подгружаются из .env/переменных окружения
4. Добавлено приложение movies `python manage.py startapp movies `
5. Прописаны модели данных `Genre, Person, FilmWork, GenreFilmWork, PersonFilmWork`
6. Добавлена миграция данных
7. Проинициализированы `Genre, Person, FilmWork` в администраторском интерфейсе

