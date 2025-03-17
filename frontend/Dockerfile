FROM node:11.15.0
#FROM node:14.15.4
#FROM node:4.7.2

LABEL maintainer="Hans-Ioan Ienasescu <hans@bio.tools>"

RUN useradd --user-group --create-home biotools

ENV HOME=/home/biotools

WORKDIR $HOME/frontend

RUN mkdir components/ css/ img/ js/ json/ lib/ partials/ resources/ static/
COPY components components/
COPY css css/
COPY img img/
COPY js js/
COPY json json/
COPY lib lib/
COPY partials partials/
COPY resources resources/
COPY static static/
COPY bower.json gulpfile.js index-async.html index.html package.json package-lock.json /home/biotools/frontend/

RUN chown -R biotools:biotools $HOME/*
USER biotools
    
RUN npm config set prefix /usr/local && npm install && export PATH="./node_modules/.bin:$PATH" && bower install

# Required to work on Linux, otherwise there are permission errors
USER root
RUN chown -R biotools:biotools $HOME/*

CMD ["node_modules/.bin/gulp"]