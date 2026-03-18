FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST=0.0.0.0
ENV REDIS_PORT=6379
ENV READ_BUFFER_SIZE=4096

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6379

CMD ["python", "-m", "src.main"]
