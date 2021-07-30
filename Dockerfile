FROM certbot/certbot:v1.3.0

COPY . /app

RUN cd /app && python setup.py install
