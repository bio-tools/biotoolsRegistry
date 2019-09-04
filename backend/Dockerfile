FROM python:2.7.15

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

# Install app and its runtime dependency.
RUN apt-get -y update \
    && apt-get install -y apache2 apache2-utils ssl-cert libapache2-mod-wsgi \
    && apt-get install -y \
        default-libmysqlclient-dev \
    && pip install -r requirements.txt \
    && rm -f requirements.txt


COPY runtime/apache.conf /etc/apache2/sites-available/elixir.conf

RUN a2enmod wsgi && a2enmod ssl && a2enmod rewrite && a2enmod proxy_http && a2ensite elixir.conf

EXPOSE 80

# remove default apache config from sites-enable so bio.tools subdomain redirect works
RUN rm /etc/apache2/sites-enabled/000-default.conf

# expose apache logs to stdout
# most logs will come from other_vhosts_access.log
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/other_vhosts_access.log

CMD /usr/sbin/apache2ctl -D FOREGROUND