# Решение проектного задания

## Состав проекта

Для развертывания проекта используется docker-compose.
Используется полная структура проекта из предыдущих спринтов.

Файл [docker-compose.yaml](https://github.com/dimk00z/Async_API_sprint_1/blob/main/docker-compose.yaml) содержит описание трех образов проекта:

1. `movies_async_api` - реализации "ручек" для доступа к Elasticsearch

2. `postges_movie_db` - образ для развертывания postgres. В текущих настройках файлы базы данных связаны с путем `../postgres`
3. `movies_admin` - образ с бэкэндом django на основе [Dockerfile_django](https://github.com/dimk00z/Async_API_sprint_1/blob/main/Dockerfile_django). При развертывании в образ устанавливаются зависимости [production.txt](https://github.com/dimk00z/Async_API_sprint_1/blob/main/movies_admin/requirements/production.txt). Сервер работает через `gunicorn`.
4. `nginx` - образ с nginx веб-сервером на основе [Dockerfile_nginx](https://github.com/dimk00z/Async_API_sprint_1/blob/main/nginx/Dockerfile_nginx) для отдачи статики и проброса с movies_admin:8000.
5. `elasticsearch` - образ с Elasticsearch v.7.14.1 для хранения поисковых индексов
6. `redis` - Redis для хранения состояния
7. `postgres_to_es` - сервис для загрузки индексов из Postgres в Elasticsearch

## Описание Async_API реализации

- [`main.py`](https://github.com/dimk00z/Async_API_sprint_1/blob/main/async_api/src/main.py) - основной скрипт для запуска под сервером uvicorn ручек на FastAPI.
- [`services`](https://github.com/dimk00z/Async_API_sprint_1/tree/main/async_api/src/services) - реализация поиска данных из Elasticsearch
- [`api/v1`](https://github.com/dimk00z/Async_API_sprint_1/tree/main/async_api/src/api/v1) - роутеры для ручек

## Запуск проекта

1. Для корректной работы необходим `.env` файл на основе `env_example`. Важно: если `ES_SHOULD_DROP_INDEX=TRUE`, то индекс и запись в redit сбросятся.
2. Предполагается, что по пути `../postgres` находятся данные из предыдущих двух спринтов: первичные миграции проведены, в базе есть данные администратора и выгружены данные из sqlite.
4. `docker-compose up -d --build` - для построения и запуска контейнеров.
Примеры запросов:
```
http://localhost:8000/api/v1/genre
http://localhost:8000/api/v1/film/?sort=-imdb_rating&filter[genre]=526769d7-df18-4661-9aa6-49ed24e9dfd8&page[size]=10&page[number]=1
http://localhost:8000/api/v1/person/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a/film
```
## Выполнили

- [Дмитрий Кузнецов](https://github.com/dimk00z)

- [Арсений Егоров](https://github.com/marchinho11)

- [Мурдашев Дмитрий](https://github.com/di3mus)



# Техническое задание

Предлагается выполнить проект «Асинхронное API». Этот сервис будет точкой входа для всех клиентов. В первой итерации в сервисе будут только анонимные пользователи. Функции авторизации и аутентификации запланированы в модуле «Auth».

## Используемые технологии

- Код приложения пишется на **Python + FastAPI**.
- Приложение запускается под управлением сервера **ASGI**(uvicorn).
- Хранилище – **ElasticSearch**.
- За кеширование данных отвечает – **redis cluster**.
- Все компоненты системы запускаются через **docker**.

## Описание
В папке tasks ваша команда сможет найти задачи, которые необходимо выполнить в первом спринте второго модуля. Обратите внимание на задачи 00_create_repo и 01_create_basis – они являются блокирующими для командной работы, их необходимо выполнить как можно раньше.

Мы оценили задачи в story point'ах, значения которых брались из [последовательности Фибоначчи](https://ru.wikipedia.org/wiki/Числа_Фибоначчи) (1,2,3,5,8,…).
Вы можете разбить имеющиеся задачи на более маленькие – например, чтобы распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

**От каждого разработчика ожидается выполнение минимум 40% от общего числа story points в спринте.**

### `make format`
```shell
pip install isort==5.9.3 black==21.7b0

make format
```