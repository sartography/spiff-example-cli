FROM python:3.10.4-slim-bullseye

COPY requirements.txt ./
COPY custom_script.py /app/custom_script.py
COPY docker.py /app/docker.py

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
