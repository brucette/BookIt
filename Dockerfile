# create's a layer from the python docker image
FROM python

ADD requirements.txt /code/
WORKDIR /code
RUN pip3 install -r requirements.txt

ENV FLASK_DEBUG true

ENTRYPOINT ["/usr/local/bin/python3","/code/app.py"]
