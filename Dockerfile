FROM python:3.10-slim
ARG user
ARG password
EXPOSE 8080
ADD ./requirements.lock /
RUN pip install -r /requirements.lock
ARG GATEWAY
ENV GATEWAY=$GATEWAY
ADD . /plugin
ENV PYTHONPATH=$PYTHONPATH:/plugin
CMD python services.py
