# NOTE - this file will be removed in a future PR, only keeping it in place
# because the initial Release integration includes a POC for how to execute
# databuilder jobs.
FROM python:3.7-slim

ENV LANG="en_US.utf8" \
    AMUNDSEN_SERVICE_NAME="databuilder"

ADD ../../ /usr/local/amundsen
WORKDIR /usr/local/amundsen

# Install python requirements
RUN cd databuilder && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    python3 setup.py install

COPY stemma/scripts/run-databuilder.sh /usr/local/amundsen/

CMD ["./run-databuilder.sh"]