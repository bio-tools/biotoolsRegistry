FROM node:24.13.1-slim
#FROM node:14.15.4

LABEL maintainer="SDU <support-bio-tools@sdu.dk>"

RUN addgroup biotools && adduser --system --group biotools
RUN chown -R biotools:biotools $HOME

USER biotools
ENV HOME=/home/biotools
WORKDIR $HOME/frontend

COPY --chown=biotools:biotools package*.json .
RUN npm install
COPY --chown=biotools:biotools . .

RUN node_modules/.bin/gulp copy css scripts bower
CMD ["node_modules/.bin/gulp"]
