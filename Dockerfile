FROM debian:stable-slim

LABEL maintainer="OmniDB-NG team"

ARG OMNIDB_VERSION=3.0.6

SHELL ["/bin/bash", "-c"]

USER root

RUN addgroup --system omnidb \
    && adduser --system omnidb --ingroup omnidb \
    && apt-get update \
    && apt-get install -y curl wget vim python3

USER omnidb:omnidb
ENV HOME /home/omnidb

WORKDIR ${HOME}

WORKDIR ${HOME}
RUN python3 -c "$(curl -fsSL https://pgsql-io-download.s3.amazonaws.com/REPO/install.py)"
WORKDIR ${HOME}/pgsql
RUN ./io install instantclient
RUN ./io install ora2pg

WORKDIR ${HOME}
RUN wget https://github.com/pgsql-io/OmniDB-NG/archive/${OMNIDB_VERSION}.tar.gz \
    && tar -xvzf ${OMNIDB_VERSION}.tar.gz \
    && mv omnidb-ng-${OMNIDB_VERSION} OmniDB

WORKDIR ${HOME}/OmniDB
RUN apt-get install -y libsasl2-dev python3-dev python3-pip libldap2-dev libssl-dev 
RUN pip3 install -r requirements.txt

WORKDIR ${HOME}/OmniDB/OmniDB
RUN sed -i "s/LISTENING_ADDRESS    = '127.0.0.1'/LISTENING_ADDRESS    = '0.0.0.0'/g" config.py \
    && python3 omnidb-server.py --init 

EXPOSE 8000

CMD python3 omnidb-server.py
