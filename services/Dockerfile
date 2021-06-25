FROM ubuntu:20.04

RUN apt-get upgrade && apt-get update \
  && apt-get install -y python3-pip python3-dev python3-venv \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && rm -fr /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
