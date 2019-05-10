FROM python:3.6-slim

RUN mkdir -p /var/bot 
COPY requirements.txt /var/bot/
RUN pip install -r /var/bot/requirements.txt

COPY *.py data.json /var/bot/

CMD [ "python", "/var/bot/bot.py" ]