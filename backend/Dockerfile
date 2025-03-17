FROM ubuntu:20.04


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


# Install Python 3.8
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y software-properties-common -y && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update -y && apt-get -y install python3.8 python3-pip

# make symlink for python3 to python
RUN ln -sf /usr/bin/python3 /usr/bin/python && ln -sf /usr/bin/pip3 /usr/bin/pip


RUN apt-get update && apt-get -y install apache2 apache2-utils ssl-cert libapache2-mod-wsgi-py3 && apt-get install -y python3-dev default-libmysqlclient-dev build-essential 

RUN pip install -r requirements.txt && rm -f requirements.txt

COPY runtime/apache.conf /etc/apache2/sites-available/elixir.conf

RUN a2enmod wsgi && a2enmod ssl && a2enmod rewrite && a2enmod proxy_http && a2ensite elixir.conf && service apache2 restart

RUN apt-get update -y && apt-get install curl

EXPOSE 80

# remove default apache config from sites-enable so bio.tools subdomain redirect works
RUN rm /etc/apache2/sites-enabled/000-default.conf

RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && ln -sf /proc/self/fd/1 /var/log/apache2/error.log && ln -sf /proc/self/fd/1 /var/log/apache2/other_vhosts_access.log

CMD /usr/sbin/apache2ctl -D FOREGROUND