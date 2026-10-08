# =========================
# FRONTEND BUILDER
# =========================
FROM node:11.15.0-slim AS frontend-builder

WORKDIR /home/biotools/frontend

# Point Stretch to the archive
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends --allow-unauthenticated \
        git \
        && rm -rf /var/lib/apt/lists/*

COPY frontend/package*.json ./
RUN npm install

RUN npm install -g bower

COPY frontend/bower.json ./
RUN bower install --allow-root

COPY frontend/ ./

RUN node_modules/.bin/gulp build


# =========================
# BUILDER
# =========================
FROM python:3.13 AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        libmariadb-dev \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /elixir/application/backend

COPY backend/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY backend/ .


# =========================
# PROD
# =========================
FROM python:3.13-slim AS prod

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /elixir/application/backend

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apache2 \
        apache2-utils \
        apache2-dev \
        ssl-cert \
        libmariadb3 \
        libapache2-mod-wsgi-py3 \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod wsgi
RUN a2enmod rewrite

COPY --from=builder /usr/local/lib/python3.13/site-packages/ \
    /usr/local/lib/python3.13/site-packages/

COPY --from=builder /usr/local/bin/ \
    /usr/local/bin/

COPY --from=builder /elixir/application/backend \
    /elixir/application/backend

COPY --from=frontend-builder \
    /home/biotools/frontend \
    /elixir/application/frontend

# Build mod_wsgi against Python 3.13
RUN pip install --no-cache-dir mod_wsgi

COPY backend/runtime/apache.conf /etc/apache2/sites-available/elixir.conf

RUN a2enmod headers ssl rewrite proxy_http && \
    a2ensite elixir.conf && \
    rm -f /etc/apache2/sites-enabled/000-default.conf && \
    ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/other_vhosts_access.log

EXPOSE 80

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
