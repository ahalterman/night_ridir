FROM ubuntu:14.04

MAINTAINER Andy Halterman <ahalterman0@gmail.com>

RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y git wget tar \
 build-essential python-dev libopenblas-dev python-numpy python-scipy
RUN apt-get install -y python-pip
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN pip install git+https://github.com/openeventdata/petrarch2/

WORKDIR /app
RUN wget https://s3.amazonaws.com/mordecai-geo/GoogleNews-vectors-negative300.bin.gz
RUN wget https://s3.amazonaws.com/ahalterman-textdata/wiki_ar_word2vec.model
RUN wget https://s3.amazonaws.com/ahalterman-textdata/wiki_ar_word2vec.model.syn0.npy
RUN wget https://s3.amazonaws.com/ahalterman-textdata/wiki_ar_word2vec.model.syn1neg.npy

#RUN mkdir /home/ubuntu
#WORKDIR /home/ubuntu

#RUN git clone https://github.com/mit-nlp/MITIE.git
#WORKDIR /home/ubuntu/MITIE
#
#RUN wget http://sourceforge.net/projects/mitie/files/binaries/MITIE-models-v0.2.tar.bz2
#RUN tar --no-same-owner -xjf MITIE-models-v0.2.tar.bz2
#RUN mkdir /home/ubuntu/MITIE/mitielib/build
#RUN cd mitielib/build; cmake ..
#RUN cd mitielib/build; cmake --build . --config Release --target install
#RUN pip install git+https://github.com/caerusassociates/mitie-py.git

ADD . /app/

EXPOSE 5000
CMD ["python", "/app/app.py"]
