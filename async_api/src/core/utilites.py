from urllib.parse import urlparse

from fastapi import Request


def get_path_from_url(url: Request) -> str:
    path = urlparse(str(url.url)).path
    if url.url.query:
        path = f"{path}?{url.url.query}"
    return path
