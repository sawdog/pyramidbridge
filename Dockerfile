FROM jfloff/alpine-python
LABEL Description="Docker container for standing up a pyramid web app to bridge Smartthings events to a rethinkDB" Maintainer="Andrew Sawyers <andrew.sawyers@sawdog.com>"
SHELL ["/bin/bash", "-c"]

# We copy this file first to leverage docker cache
COPY src /app/

WORKDIR /app

RUN pip install -U pip && \
    pip install -r requirements.txt && \
    python setup.py install

ENTRYPOINT [ "pserve" ]

CMD [ "/app/production.ini" ]
