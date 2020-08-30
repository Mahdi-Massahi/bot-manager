FROM python:3.8
MAINTAINER Nebix Team (Mohammad Salek)
ENV PYTHONUNBUFFERED 1

RUN mkdir /root/.ssh/
# secrets folder is needed:
ADD secrets/id_ed25519 /root/.ssh/id_ed25519
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts

RUN mkdir /nebix
WORKDIR /nebix

# RUN git clone git@gitlab.com:mohammadsalek/nebix-trading-bot.git
# WORKDIR /nebix/nebix-trading-bot

RUN mkdir nebix-trading-bot
WORKDIR /nebix/nebix-trading-bot
COPY . .

RUN rm -rf secrets/
RUN bash install.sh

RUN git config remote.origin.url git@gitlab.com:mohammadsalek/nebix-trading-bot.git
