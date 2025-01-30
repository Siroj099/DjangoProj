FROM python:3.10.5-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz | tar -xzv && \
    mv dockerize /usr/local/bin/dockerize

RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    libpq-dev \
    && apt-get clean

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT ["dockerize", "-wait", "tcp://db:5432", "-timeout", "60s", "python", "manage.py", "runserver", "0.0.0.0:8080"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]