FROM python:3.10.4-slim-bullseye

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD . .

ENTRYPOINT [ "python", "./run.py" ]
