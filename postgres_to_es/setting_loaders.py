import logging
from typing import Tuple

from pydantic import BaseSettings, Field
from pydantic.error_wrappers import ValidationError


class PostgresSettings(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_DB")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field(..., env="POSTGRES_HOST")
    port: str = Field(..., env="POSTGRES_PORT")
    options: str = "-c search_path=content"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ElasticSettings(BaseSettings):
    host: str = Field(..., env="ES_HOST")
    index: str = Field(..., env="ES_INDEX")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    host: str = Field(..., env="REDIS_HOST")
    port: str = Field(..., env="REDIS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_etl_settings() -> Tuple[PostgresSettings, ElasticSettings, RedisSettings]:
    try:
        return (PostgresSettings(), ElasticSettings(), RedisSettings())
    except ValidationError:
        logging.error("Could load settings from enviromentals or .env")
        raise SystemExit
