FROM python:3.11-slim

WORKDIR /app

COPY sysmon-generator.py /app/

RUN mkdir -p /sysmon-logs

CMD ["python", "-u", "sysmon-generator.py"]
