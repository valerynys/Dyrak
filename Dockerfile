FROM python:3.7-slim

WORKDIR /durakbot

COPY requirements.txt /durakbot/
RUN pip install -r /durakbot/requirements.txt
COPY . /durakbot/

CMD python3 /durakbot/bot.py
