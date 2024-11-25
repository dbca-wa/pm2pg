FROM python:slim
RUN apt-get update && apt-get install -y libpq-dev

# Create a non-root user
RUN useradd -m appuser

ADD . /python-flask
WORKDIR /python-flask

# Change ownership of the application directory
RUN chown -R appuser:appuser /python-flask

# Switch to the non-root user
USER appuser

EXPOSE 5443
RUN pip install -r requirements.txt
CMD [ "python3", "pm_webhook.py"]
