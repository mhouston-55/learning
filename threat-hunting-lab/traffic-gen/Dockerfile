FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    dnsutils \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install flask requests

COPY *.py /app/

EXPOSE 8888

CMD ["python", "-u", "control-server.py"]
