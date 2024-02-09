FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y git sqlite3

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD . .

ENTRYPOINT [ "./runner.py -e spiff_example.spiff.file" ]
