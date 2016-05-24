FROM ubuntu:14.04

MAINTAINER Andy Halterman <ahalterman0@gmail.com>

RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y git wget tar \
 build-essential python-dev libopenblas-dev python-numpy python-scipy
RUN apt-get install -y python-pip
COPY . /app/
RUN pip install -r /app/requirements.txt
RUN pip install git+https://github.com/openeventdata/petrarch2/

WORKDIR /app
RUN wget https://s3.amazonaws.com/mordecai-geo/GoogleNews-vectors-negative300.bin.gz
RUN wget https://s3.amazonaws.com/ahalterman-textdata/wiki_ar_word2vec.model
RUN wget https://s3.amazonaws.com/ahalterman-textdata/wiki_ar_word2vec.model.syn0.npy
RUN wget https://s3.amazonaws.com/ahalterman-textdata/wiki_ar_word2vec.model.syn1neg.npy

EXPOSE 5000
CMD ["python", "/app/app.py"]
