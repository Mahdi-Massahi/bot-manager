FROM python:3.8
MAINTAINER Nebix Team (Mohammad Salek)
ENV PYTHONUNBUFFERED 1

RUN apt-get install -y git
RUN pip install --upgrade pip

RUN mkdir /root/.ssh/
ADD secrets/id_ed25519 /root/.ssh/id_ed25519
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts

RUN mkdir /nebix
WORKDIR /nebix

RUN git clone git@gitlab.com:mohammadsalek/nebix-trading-bot.git

WORKDIR /nebix/nebix-trading-bot

RUN rm -rf secrets/

RUN pip3 install -r requirements.txt
RUN bash install.sh

WORKDIR /nebix/nebix-trading-bot/env/lib/python3.8/site-packages/nebixbm/
