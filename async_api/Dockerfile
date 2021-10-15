FROM python:3.9.5-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY /src/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY /src /code
WORKDIR /code

CMD uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --use-colors
