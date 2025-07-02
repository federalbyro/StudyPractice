FROM python:3.12-slim

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.sh .
RUN chmod +x run.sh
COPY src/ ./src
ENV PYTHONPATH=/app

ENTRYPOINT ["sh", "run.sh"]
