FROM python:3.8
MAINTAINER Nebix Team (Mohammad Salek)
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y r-base vim
RUN python -m pip install --upgrade pip

RUN mkdir /root/.ssh/
ADD secrets/id_ed25519 /root/.ssh/id_ed25519
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts
RUN chmod 400 /root/.ssh/id_ed25519

WORKDIR /nbm/
RUN git clone git@gitlab.com:mohammadsalek/nebix-trading-bot.git
WORKDIR /nbm/nebix-trading-bot

RUN rm -rf secrets/
RUN rm -rf doc/
RUN rm README.md
RUN rm -rf README.md

RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN git config remote.origin.url git@gitlab.com:mohammadsalek/nebix-trading-bot.git
