FROM python:3.8-slim-buster

ARG TARGET_CONFIG
RUN test -n "$TARGET_CONFIG" || (echo "Provide a TARGET_CONFIG build arg" && false)

# Install common
COPY ../../common /tmp/common
COPY ../../requirements-common.txt /tmp/common/requirements-common.txt
COPY ../../requirements-dev.txt /tmp/common/requirements-dev.txt
RUN pip install -r /tmp/common/requirements.txt && pip install /tmp/common && rm -r /tmp/common

WORKDIR /app
COPY ../../stemma/deploy_configs/ /app/
RUN find ./customers -maxdepth 1 -type f ! -regex '^./customers/'$TARGET_CONFIG'.py$' -delete
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "build_configs.py" ]
