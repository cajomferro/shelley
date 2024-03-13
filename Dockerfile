# pull official base image
FROM python:3.11-slim-bookworm

# Update repo index
RUN apt-get update -y

# Install required build dependencies
RUN apt-get install -y wget git graphviz vim nano emacs

WORKDIR /opt

# install NuSMV
RUN mkdir nusmv
RUN wget http://nusmv.fbk.eu/distrib/NuSMV-2.6.0-zchaff-linux64.tar.gz && \
    tar -xvzf NuSMV-2.6.0-zchaff-linux64.tar.gz -C nusmv --strip-components=1
RUN cd nusmv/bin && \
    ln -s NuSMV nusmv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=0
ENV POETRY_VIRTUALENVS_CREATE=0
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# set work directory
WORKDIR /app

# Copy project
COPY . .

ARG CACHEBUST=1

RUN pip install --upgrade pip
RUN pip install poetry==1.8.2

#RUN poetry install && rm -rf $POETRY_CACHE_DIR
