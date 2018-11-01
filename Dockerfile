# x86 architecture 
FROM debian:jessie
RUN apt-get upgrade && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
	    python \
	    build-essential \
	    gcc \
	    python-dev \ 
	    python-flask \
	    libffi-dev \
	    python-pip

EXPOSE 5000

# server 
RUN     pip install --upgrade pip &&  \
        pip install --upgrade setuptools && \
        pip install google-api-python-client && \
        pip install pyCrypto && \
        pip install six && \
        pip install oauth2client && \
        apt-get install -y libssl-dev
RUN     pip install earthengine-api
ADD     static /home/static 
ADD     templates /home/templates
COPY    app.py /home/app.py
RUN     chmod +x /home/app.py

WORKDIR /home
CMD     /bin/bash