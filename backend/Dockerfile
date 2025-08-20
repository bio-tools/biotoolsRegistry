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


# Second stage
# Uses packages and binaries from builder, but is smaller and runs as a non-root user
FROM python:3.13-slim

LABEL maintainer="SDU <support-bio-tools@sdu.dk>"

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
