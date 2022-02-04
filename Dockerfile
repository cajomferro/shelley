# pull official base image
FROM python:3.10-slim

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update repo index
RUN apt-get update -y

# Install required build dependencies
RUN apt-get install -y build-essential python3-dev musl-dev libpq-dev libffi-dev curl git


## Install Pillow deps
#RUN apt-get -y install zlib1g zlib1g-dev libjpeg-dev libjpeg-turbo-progs \
#    libjpeg62-turbo libjpeg62-turbo-dev

# Remove buld essential
RUN apt-get remove -y build-essential

# Install and upgrade required python deps
RUN python -m pip install -U cffi pip setuptools \
    && pip install --upgrade pip-tools pip setuptools

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy project
COPY . .

ARG COMMIT_HASH
ENV COMMIT_HASH=${COMMIT_HASH}

# Install project dependencies (using poetry)
RUN poetry config virtualenvs.create false --local # disable poetry virtualenvs
RUN poetry install
