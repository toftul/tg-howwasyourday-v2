FROM python:3.10-bookworm

WORKDIR /bot

COPY . . 

RUN pip install -r requirements.txt

WORKDIR /bot/howwasyourdaybot

CMD [ "python", "bot.py"]