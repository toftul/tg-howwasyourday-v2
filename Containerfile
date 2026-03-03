FROM python:3.11-slim-bookworm

WORKDIR /bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /bot/howwasyourdaybot

CMD [ "python", "bot.py"]