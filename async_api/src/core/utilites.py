from urllib.parse import urlparse

from fastapi import Request


def get_path_from_url(url: Request) -> str:
    return str(urlparse(str(url.url)).path)
