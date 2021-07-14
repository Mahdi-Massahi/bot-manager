FROM python:3.8
LABEL MAINTAINER Nebix Team (Mohammad Salek)
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y r-base vim csvtool libgit2-dev tmux
RUN python -m pip install --upgrade pip

# R stuffs
RUN R -e "install.packages('devtools', dependencies=TRUE)"
#RUN R -e "devtools::install_version(package='rredis', version='1.7.0')"
#RUN R -e "devtools::install_version(package='xts', version='0.12.1')"
#RUN R -e "devtools::install_version(package='zoo', version='1.8-8')"
#RUN R -e "devtools::install_version(package='rmarkdown', version='2.5')"
RUN R -e "install.packages('rredis', dependencies=TRUE)"
RUN R -e "install.packages('xts', dependencies=TRUE)"
RUN R -e "install.packages('zoo', dependencies=TRUE)"
RUN R -e "install.packages('rmarkdown', dependencies=FALSE)"
RUN R -e "install.packages('txtplot', dependencies=FALSE)"

RUN mkdir /root/.ssh/
ADD secrets/id_ed25519 /root/.ssh/id_ed25519
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts
RUN chmod 400 /root/.ssh/id_ed25519

# ON LOCAL BEGIN
RUN mkdir -p /nebix/nbm
WORKDIR /nebix/nbm
COPY . .
# END

# ON SERVER BEGIN
#WORKDIR /nebix/
#RUN git clone git@gitlab.com:nebix-group/nbm.git
#WORKDIR /nebix/nbm
# END

RUN rm -rf secrets/
RUN rm -rf doc/
RUN rm README.md
RUN rm -rf README.md

RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN git config remote.origin.url git@gitlab.com:nebix-group/nbm.git
