FROM python:3.10-slim-bookworm

WORKDIR /bot

COPY . . 

RUN pip install -r requirements.txt

WORKDIR /bot/howwasyourdaybot

CMD [ "python", "bot.py"]