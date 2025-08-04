FROM node:11.15.0-slim
#FROM node:14.15.4
#FROM node:4.7.2

LABEL maintainer="Hans-Ioan Ienasescu <hans@bio.tools>"

RUN addgroup app && adduser --system --group app

USER app
WORKDIR /app

COPY --chown=app:app package*.json .
RUN npm install
COPY --chown=app:app . .

CMD ["node_modules/.bin/gulp"]
