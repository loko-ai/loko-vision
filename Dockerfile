FROM node:16.15.0 AS builder
COPY ./frontend/package.json /frontend/package.json
WORKDIR /frontend
RUN yarn install
COPY ./frontend /frontend
RUN yarn build --base="/routes/loko-vision/web/"

FROM python:3.10-slim
ARG user
ARG password
EXPOSE 8080
COPY ./requirements.lock /
RUN  pip install -r /requirements.lock
ARG GATEWAY
ARG PORT
ENV PORT 8080
ENV GATEWAY=$GATEWAY
COPY . /plugin
ENV PYTHONPATH=$PYTHONPATH:/plugin
COPY --from=builder /frontend/dist /frontend/dist
WORKDIR /plugin/services
CMD  python services.py --single_process
