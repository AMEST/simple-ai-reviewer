FROM python:3.12-slim-bookworm
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
    && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y tzdata\
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/ \
    && pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt 

COPY . /app
ENV RUN_IN_DOCKER=true
ENTRYPOINT ["python3","main.py"]