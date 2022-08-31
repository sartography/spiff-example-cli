import json
from celery import Celery
from kombu.serialization import register

from .custom_script import custom_data_converter

def dumps(obj):
    dct = custom_data_converter.convert(obj)
    return json.dumps(dct)

def loads(s):
    dct = json.loads(s)
    return custom_data_converter.restore(dct)

register('json', dumps, loads, content_type='application/x-json')

app = Celery('engine',
    broker='redis://localhost:6379/0',
    backend='rpc://',
    include=['engine.tasks'])

app.conf.update(results_expires=3600)

if __name__ == '__main__':
    app.start()

