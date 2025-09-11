FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip wheel setuptools

COPY ./requirements.txt .

RUN pip install -r requirements.txt && \
    pip install "gunicorn"

COPY . /app

COPY entrypoints.sh /entrypoints.sh
RUN chmod +x /entrypoints.sh

ENTRYPOINT ["/entrypoints.sh"]

EXPOSE 8001
