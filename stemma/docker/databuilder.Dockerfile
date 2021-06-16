FROM python:3.7-slim-buster

WORKDIR /app

# Install Microsoft SQL Driver
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/8/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get install apt-transport-https \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc-dev \
    && apt-get clean


RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install build-essential gcc python3-dev default-libmysqlclient-dev -y


COPY ./../../common /tmp/common
COPY ./../../requirements-common.txt /tmp/common/requirements-common.txt
COPY ./../../requirements-dev.txt /tmp/common/requirements-dev.txt
RUN pip install -r /tmp/common/requirements.txt && pip install /tmp/common/ && rm -r /tmp/common

COPY ./../../databuilder/requirements.txt /app/requirements.txt
COPY ./../../databuilder/requirements-dev.txt /app/requirements-dev.txt
RUN pip3 install -r requirements.txt

COPY ./../../databuilder/ /app

RUN pip install /app[rds,snowflake]
# RUN pip install /app[all]

RUN pip install certifi==2019.11.28 --upgrade

ENTRYPOINT [ "python3", "databuilder/stemma/tasks/run_databuilder.py" ]
