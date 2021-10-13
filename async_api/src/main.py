import logging

import uvicorn
from core import config
from db import connections
from fastapi import FastAPI
from core.logger import LOGGING
from api.v1 import film, genre, person
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    await connections.init_connectons()


@app.on_event("shutdown")
async def shutdown():
    await connections.close_connections()


# Подключаем роутер к серверу, указав префикс /v1/film
# Теги указываем для удобства навигации по документации
app.include_router(film.router, prefix="/api/v1/film", tags=["film"])
app.include_router(person.router, prefix="/api/v1/person", tags=["person"])
app.include_router(genre.router, prefix="/api/v1/genre", tags=["genre"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
