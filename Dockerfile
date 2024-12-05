FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV DOCKER 1

WORKDIR /app

RUN pip install pipenv
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy --clear

COPY . .
