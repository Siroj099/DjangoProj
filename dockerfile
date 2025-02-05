FROM python:3.10.5-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y curl postgresql-client

RUN curl -sSL https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz | tar -xz -C /usr/local/bin

RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    libpq-dev \
    && apt-get clean

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

RUN ls -lah /usr/local/bin/dockerize && dockerize --version

ENTRYPOINT ["dockerize", "-wait", "tcp://db:5432", "-timeout", "60s"]

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8080"]