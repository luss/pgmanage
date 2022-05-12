FROM debian:stable-slim

LABEL maintainer="OmniDB-NG team"

ARG OMNIDB_VERSION=3.0.6

SHELL ["/bin/bash", "-c"]

USER root

RUN addgroup --system omnidb && adduser --system omnidb --ingroup omnidb
RUN apt update
RUN apt install -y curl wget vim python3 sudo
RUN apt install -y libsasl2-dev python3-dev python3-pip libldap2-dev libssl-dev 

WORKDIR /
RUN python3 -c "$(curl -fsSL https://pgsql-io-download.s3.amazonaws.com/REPO/install.py)"
RUN /pgsql/io install instantclient 21.6

ENV ORACLE_HOME=/opt/instantclient_21_6
ENV LD_LIBRARY_PATH=${ORACLE_HOME}
ENV PATH=/usr/local/bin:/home/omnidb/.local/bin:$ORACLE_HOME:$PATH
RUN /pgsql/io install ora2pg

USER omnidb:omnidb
ENV HOME /home/omnidb

WORKDIR ${HOME}
RUN wget https://github.com/pgsql-io/OmniDB-NG/archive/${OMNIDB_VERSION}.tar.gz \
    && tar -xf ${OMNIDB_VERSION}.tar.gz \
    && mv omnidb-ng-${OMNIDB_VERSION} OmniDB

WORKDIR ${HOME}/OmniDB
RUN pip3 install -r requirements.txt

WORKDIR ${HOME}/OmniDB/OmniDB
RUN sed -i "s/LISTENING_ADDRESS    = '127.0.0.1'/LISTENING_ADDRESS = '0.0.0.0'/g" config.py \
    && python3 omnidb-server.py --init 

EXPOSE 8000

CMD python3 omnidb-server.py
