FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://get.docker.com | sh

RUN which docker || (echo "Docker not found" && exit 1)

WORKDIR /app
COPY .env .env
COPY requirements requirements
RUN pip install --no-cache-dir -r requirements/prod.txt

COPY supervisord.conf /etc/supervisor/supervisord.conf

COPY hackathon .

CMD ["supervisord", "-n"]