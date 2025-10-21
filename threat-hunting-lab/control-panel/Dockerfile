FROM python:3.11-slim

WORKDIR /app

RUN pip install flask requests

COPY app.py /app/
COPY templates /app/templates/

EXPOSE 8000

CMD ["python", "-u", "app.py"]
