FROM python:slim
RUN apt-get update && apt-get install -y libpq-dev
ADD . /python-flask
EXPOSE 5443
WORKDIR /python-flask
RUN pip install -r requirements.txt
CMD [ "python3", "PMwebhook.py"]
