FROM python:3.8-slim
RUN pip3 install gunicorn

ENV LANG="en_US.utf8" \
    AMUNDSEN_SERVICE_NAME="search" \
    SEARCH_SVC_CONFIG_MODULE_CLASS="search_service.stemma.config.StemmaConfig"

# use sock
ENV GUNICORN_BIND="0.0.0.0:5001" \
    GUNICORN_TIMEOUT=60 \
    GUNICORN_WORKERS=2

ENV GUNICORN_CMD_ARGS="--bind=${GUNICORN_BIND} --timeout=${GUNICORN_TIMEOUT} --workers=${GUNICORN_WORKERS} --access-logfile - -"

ADD ./../search /usr/local/amundsen/search
WORKDIR /usr/local/amundsen/search/

# Remove the amundsen-common from requirements
RUN sed -E -i 's/amundsen-common==(.+)//' requirements.txt

# FixMe: Please remove once below packages are fixed in amundsen OSS.
# (This is because we are using Python 3.8 in Stemma)
RUN sed -E -i 's/mypy==(.+)/mypy==0.782/' requirements.txt
RUN sed -E -i 's/Werkzeug==(.+)/Werkzeug==2.0.1/' requirements.txt

# Install the local copy of amundsen frontend
RUN pip install -e .

# Install the stemma requirements
RUN pip install -r stemma_requirements.txt

# Install requirements with local common
COPY ./../common /tmp/common
RUN pip3 install /tmp/common && rm -r /tmp/common

ENV FLASK_DEBUG 0
ENV FLASK_ENV production

EXPOSE 5001

ENTRYPOINT ["gunicorn"]
CMD ["search_service.search_wsgi:application"," --timeout 1800", "--preload"]
