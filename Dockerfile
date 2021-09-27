# pull official base image
FROM python:3.8-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add git gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv lock --requirements > /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# copy project
COPY . .
