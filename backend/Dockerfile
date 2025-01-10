FROM ubuntu:24.04

LABEL maintainer="Hans-Ioan Ienasescu <hans@bio.tools>"

# Disable buffering for logs.
ENV PYTHONUNBUFFERED 1

# Set up working directory and files.
WORKDIR /elixir/application/backend
RUN mkdir data/ elixir/ elixirapp/ runtime/ templates/
COPY requirements.txt EDAM_obsolete.json imports.sql manage.py /elixir/application/backend/
COPY data data/
COPY elixir elixir/
COPY elixirapp elixirapp/
COPY runtime runtime/
COPY templates templates/


# Install system dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    software-properties-common \
    apache2 \
    apache2-utils \
    ssl-cert \
    libapache2-mod-wsgi-py3 \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    python3-pip \
    python3-venv \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to avoid system package conflicts
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -f requirements.txt

RUN . /opt/venv/bin/activate

COPY runtime/apache.conf /etc/apache2/sites-available/elixir.conf

RUN a2enmod headers && a2enmod wsgi && a2enmod ssl && a2enmod rewrite && a2enmod proxy_http && a2ensite elixir.conf && service apache2 restart

EXPOSE 80

# remove default apache config from sites-enable so bio.tools subdomain redirect works
RUN rm /etc/apache2/sites-enabled/000-default.conf

RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && ln -sf /proc/self/fd/1 /var/log/apache2/error.log && ln -sf /proc/self/fd/1 /var/log/apache2/other_vhosts_access.log

CMD /usr/sbin/apache2ctl -D FOREGROUND