FROM python:3.10-slim
ARG user
ARG password
EXPOSE 8080
ADD ./requirements.lock /
RUN pip install -r /requirements.lock
ENV XLA_FLAGS=--xla_gpu_cuda_data_dir=/usr/local/cuda-11.5
ARG GATEWAY
ENV GATEWAY=$GATEWAY
ADD . /plugin
ENV PYTHONPATH=$PYTHONPATH:/plugin
WORKDIR /plugin/services
CMD python services.py
