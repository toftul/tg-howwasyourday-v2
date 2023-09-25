FROM python:3.10-bookworm

WORKDIR /bot

COPY . . 

RUN pip install -r requirements.txt

CMD [ "python", "bot.py"]