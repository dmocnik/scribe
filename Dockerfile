FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get -y --no-install-recommends install \
    wget \
    unzip \
    nano \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

LABEL org.opencontainers.image.title="Scribe"
LABEL org.opencontainers.image.description="Upload and transcribe videos using AI, then convert to a note doc!"
LABEL org.opencontainers.image.source="https://github.com/PhysCorp/scribe"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.version="2024.2.4.0"

EXPOSE 5000
EXPOSE 8080

CMD ["python3", "main.py", "webserver=True"]
