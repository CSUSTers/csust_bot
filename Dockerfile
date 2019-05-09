FROM python:3.6-slim

RUN mkdir -p /var/bot 
COPY *.py data.json requirements.txt /var/bot/

RUN pip install -r /var/bot/requirements.txt

CMD [ "python", "/var/bot/bot.py" ]