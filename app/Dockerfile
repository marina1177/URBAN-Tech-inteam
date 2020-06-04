FROM python:3.8.0-slim-buster
MAINTAINER S. Guliaev <semen.guliaev@gmail.com>

RUN apt-get update -yq
RUN apt-get install -yq libpq-dev postgresql postgresql-contrib
RUN apt-get install -yq gcc
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["sh", "entrypoint.sh"]
