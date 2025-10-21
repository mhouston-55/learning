FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY app.py /app/
COPY templates /app/templates/

EXPOSE 8080

CMD ["python", "app.py"]
