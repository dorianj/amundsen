# Building and Copying frontend resources
FROM node:12-slim as builder
WORKDIR /usr/local/amundsen/frontend/amundsen_application/static

COPY ./../../frontend/amundsen_application/static/package.json /usr/local/amundsen/frontend/amundsen_application/static/package.json
COPY ./../../frontend/amundsen_application/static/package-lock.json /usr/local/amundsen/frontend/amundsen_application/static/package-lock.json
RUN npm install

COPY ./../../frontend/amundsen_application/static /usr/local/amundsen/frontend/amundsen_application/static
RUN npm run build

FROM python:3.8-slim
RUN pip3 install gunicorn

ENV LANG="en_US.utf8" \
    AMUNDSEN_SERVICE_NAME="frontend" \
    FRONTEND_SVC_CONFIG_MODULE_CLASS="amundsen_application.stemma.config.StemmaConfig"

# use sock
ENV GUNICORN_BIND="0.0.0.0:5000" \
    GUNICORN_TIMEOUT=60 \
    GUNICORN_WORKERS=2

ENV GUNICORN_CMD_ARGS="--bind=${GUNICORN_BIND} --timeout=${GUNICORN_TIMEOUT} --workers=${GUNICORN_WORKERS} --access-logfile - -"

ADD ./../../frontend /usr/local/amundsen/frontend
# Add the common requirements
ADD ./../../requirements-common.txt /usr/local/amundsen/frontend/requirements-common.txt
ADD ./../../requirements-dev.txt /usr/local/amundsen/frontend/requirements-dev.txt
WORKDIR /usr/local/amundsen/frontend/

ENV PYTHONPATH=$PYTHONPATH:/usr/local/amundsen/frontend

# Remove the amundsen-common from requirements
RUN sed -E -i 's/amundsen-common[>=]=(.+)//' requirements-common.txt

# Install the local copy of amundsen frontend
RUN pip install -e .

# Install the stemma requirements
RUN pip install -r stemma_requirements.txt

# Install requirements with local common
COPY ./../../common /tmp/common
COPY ./../../requirements-common.txt /tmp/common/requirements-common.txt
COPY ./../../requirements-dev.txt /tmp/common/requirements-dev.txt
RUN pip3 install /tmp/common && rm -r /tmp/common

ENV FLASK_DEBUG 0
ENV FLASK_ENV production

COPY --from=builder /usr/local/amundsen/frontend /usr/local/amundsen/frontend

EXPOSE 5000

ENTRYPOINT ["gunicorn"]
CMD ["amundsen_application.wsgi:application"," --timeout 1800", "--preload"]
