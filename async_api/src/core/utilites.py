from urllib.parse import urlparse

from fastapi import Request


def get_path_from_request(req: Request) -> str:
    path = urlparse(str(req.url)).path
    if req.url.query:
        path = f"{path}?{req.url.query}"
    return path
