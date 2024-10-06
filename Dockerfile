ARG PYTHON_VERSION=3.12.4
FROM docker-proxy.kontur.host/python:${PYTHON_VERSION}-slim AS base
ENV PYTHONUTF8=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY /src src

COPY requirements.txt .

#COPY alembic.ini .

RUN apt-get update && apt-get install -y locales

RUN dpkg-reconfigure locales && locale-gen C.UTF-8 && /usr/sbin/update-locale LANG=C.UTF-8

RUN echo 'ru_RU.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen

ENV LC_ALL ru_RU.UTF-8

RUN python -m pip install -r requirements.txt

#RUN --mount=type=secret,id=pg_pass,required ls -la /run/secrets/

EXPOSE 8080

#CMD python -m alembic upgrade head && cd src && python -m main
CMD cd src && python -m main

