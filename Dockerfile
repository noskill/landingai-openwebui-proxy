FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    GUNICORN_TIMEOUT=600

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

EXPOSE 8080

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:8080 --timeout ${GUNICORN_TIMEOUT} app:app"]
