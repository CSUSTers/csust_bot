FROM python:3.6

RUN curl https://bootstrap.pypa.io/get-pip.py | python
RUN mkdir /var/bot 
COPY requirements.txt /var/bot/
RUN pip install -r /var/bot/requirements.txt

COPY *.py /var/bot/
COPY data.json /var/bot/

CMD [ "python", "/var/bot/bot.py" ]