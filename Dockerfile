FROM node:22-bookworm-slim AS modern-assets
WORKDIR /assets/frontend-modern
COPY frontend-modern/package*.json ./
RUN npm ci
COPY frontend-modern/ ./
COPY backend/elixir/resource-contract.generated.ts /assets/backend/elixir/resource-contract.generated.ts
COPY backend/elixir/biotoolsSchema/resource-ui.generated.json /assets/backend/elixir/biotoolsSchema/resource-ui.generated.json
COPY backend/elixirapp/tests/data/ /assets/backend/elixirapp/tests/data/
RUN npm run type-check && npm run build

# PROD STAGE
# Apache + mod_wsgi
FROM ubuntu:22.04 AS runtime

LABEL maintainer="SDU support-bio-tools@sdu.dk"
ENV PYTHONUNBUFFERED=1
ENV BIOTOOLS_MIGRATION_PREVIEW_DEMOS=0
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /elixir/application/backend

# Install Python + Apache + mod_wsgi
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev default-libmysqlclient-dev build-essential \
                       apache2 apache2-utils ssl-cert libapache2-mod-wsgi-py3 curl && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip


# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

# Keep source and assets in the image; production does not mount the checkout.
COPY backend/ /elixir/application/backend/

# Apache config
COPY backend/runtime/apache-native.conf /etc/apache2/sites-available/elixir.conf
RUN a2enmod headers wsgi ssl rewrite proxy_http && \
    a2ensite elixir.conf && \
    rm /etc/apache2/sites-enabled/000-default.conf && \
    ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/other_vhosts_access.log

EXPOSE 80
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]

FROM runtime AS prod
COPY registry-assets/resources/ /elixir/application/frontend/resources/
COPY registry-assets/img/ /elixir/application/frontend/img/
COPY registry-assets/json/ /elixir/application/frontend/json/
COPY --from=modern-assets /assets/backend/elixir/static/modern /elixir/application/backend/elixir/static/modern
RUN python manage.py collectstatic --noinput && mkdir -p /elixir/application/robots /elixir/application/media_cdn && printf 'User-agent: *\nDisallow: /\n' > /elixir/application/robots/robots-deny-all.txt

