FROM python:3.6.1-slim

MAINTAINER Sean A. Leeka <sleeka@swbell.net>

RUN mkdir /api
COPY api.py /api
COPY ./requirements.txt /api

WORKDIR /api

RUN pip3 install -r requirements.txt

#EXPOSE 5000
#ENTRYPOINT ["python", "/api/api.py"]