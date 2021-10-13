FROM python:3.9.5-slim-buster

WORKDIR /code
COPY /src .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --use-colors
