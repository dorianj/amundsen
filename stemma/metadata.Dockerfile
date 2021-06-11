FROM python:3.8-slim
RUN pip3 install gunicorn

ENV LANG="en_US.utf8" \
    AMUNDSEN_SERVICE_NAME="metadata" \
    METADATA_SVC_CONFIG_MODULE_CLASS="metadata_service.stemma.config.StemmaConfig"

# use sock
ENV GUNICORN_BIND="0.0.0.0:5002" \
    GUNICORN_TIMEOUT=60 \
    GUNICORN_WORKERS=2

ENV GUNICORN_CMD_ARGS="--bind=${GUNICORN_BIND} --timeout=${GUNICORN_TIMEOUT} --workers=${GUNICORN_WORKERS} --access-logfile - -"

ADD ./../metadata /usr/local/amundsen/metadata
WORKDIR /usr/local/amundsen/metadata/

# Remove the amundsen-common from requirements
RUN sed -E -i 's/amundsen-common[>=]=(.+)//' requirements.txt

# Install the local copy of amundsen frontend
RUN pip install -e .

# Install the stemma requirements
RUN pip install -r stemma_requirements.txt

# Install requirements with local common
COPY ./../common /tmp/common
RUN pip3 install /tmp/common && rm -r /tmp/common

ENV FLASK_DEBUG 0
ENV FLASK_ENV production

EXPOSE 5002

ENTRYPOINT ["gunicorn"]
CMD ["metadata_service.metadata_wsgi:application"," --timeout 1800", "--preload"]
