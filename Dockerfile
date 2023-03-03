FROM python:3.8.18

SHELL ["/bin/bash", "--login", "-c"]

WORKDIR /app/
ENV PYTHONUNBUFFERED=1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV LANGUAGE=C.UTF-8

RUN apt-get update && \
    apt-get install -yq build-essential ca-certificates locales

RUN curl -sSL https://install.python-poetry.org | python -
RUN /root/.local/bin/poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./

RUN /root/.local/bin/poetry install

ADD ./ ./

RUN python manage.py migrate
CMD python manage.py runserver 0.0.0.0:8000
