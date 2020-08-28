FROM python:3.8
MAINTAINER Nebix Team (Mohammad Salek)
ENV PYTHONUNBUFFERED 1

RUN apt-get install -y git

RUN mkdir /root/.ssh/
ADD secrets/id_ed25519 /root/.ssh/id_ed25519
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts

RUN mkdir /temp
WORKDIR /temp

RUN git clone git@gitlab.com:mohammadsalek/nebix-trading-bot.git

WORKDIR /temp/nebix-trading-bot

RUN pip install -r requirements.txt
RUN pip install .
