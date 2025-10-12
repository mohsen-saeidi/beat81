FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# Ensure the data directory exists inside the container
RUN mkdir -p /app/data

CMD ["python", "beat81/tg_bot.py"]
