FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt update
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 -r requirements.txt
COPY . /code/