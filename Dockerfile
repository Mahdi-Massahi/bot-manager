FROM python:3.8
MAINTAINER Nebix Team (Mohammad Salek)
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y r-base vim
# TODO: requirements for r-base

RUN mkdir /root/.ssh/
# secrets folder is needed:
ADD secrets/id_ed25519 /root/.ssh/id_ed25519
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts
RUN chmod 400 /root/.ssh/id_ed25519

RUN mkdir /nebix
WORKDIR /nebix
RUN git clone git@gitlab.com:mohammadsalek/nebix-trading-bot.git
WORKDIR /nebix/nebix-trading-bot

#RUN mkdir -p /nebix/nebix-trading-bot
#WORKDIR /nebix/nebix-trading-bot
#COPY . .

RUN rm -rf secrets/
RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN git config remote.origin.url git@gitlab.com:mohammadsalek/nebix-trading-bot.git
