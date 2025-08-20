FROM node:11.15.0-slim
#FROM node:14.15.4

LABEL maintainer="SDU <support-bio-tools@sdu.dk>"

RUN addgroup app && adduser --system --group app

USER app
WORKDIR /app

COPY --chown=app:app package*.json .
RUN npm install
COPY --chown=app:app . .

CMD ["node_modules/.bin/gulp"]
