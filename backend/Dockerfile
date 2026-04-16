# BASE STAGE
FROM python:3.13 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /elixir/application/backend
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .


# DEV STAGE
# Uses packages and binaries from builder, but is smaller and runs as a non-root user
FROM python:3.13-slim AS dev

ENV PYTHONUNBUFFERED=1

RUN useradd -m -r appuser

# Install MySql dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /elixir/application/backend /elixir/application/backend

RUN chown -R appuser:appuser /elixir/application/backend
WORKDIR /elixir/application/backend
USER appuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# PROD STAGE
# Apache + mod_wsgi
FROM python:3.13-slim AS prod

LABEL maintainer="SDU support-bio-tools@sdu.dk"
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /elixir/application/backend

# Install Apache + mod_wsgi + MySQL client libraries
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    apache2 \
    apache2-utils \
    libapache2-mod-wsgi-py3 \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages and application from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /elixir/application/backend /elixir/application/backend

# Apache config
COPY runtime/apache.conf /etc/apache2/sites-available/elixir.conf
RUN a2enmod headers wsgi ssl rewrite proxy_http && \
    a2ensite elixir.conf && \
    rm /etc/apache2/sites-enabled/000-default.conf && \
    ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/other_vhosts_access.log

EXPOSE 80
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
