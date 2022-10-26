from celery import Celery
from kombu.serialization import register

from .custom_script import dumps, loads, get_globals

register('json', dumps, loads, content_type='application/x-json')

app = Celery('engine',
    broker='redis://localhost:6379/0',
    backend='rpc://')

@app.task
def evaluate(expression, context, external_methods):
    return eval(expression, get_globals(context, external_methods))

@app.task
def execute(script, context, external_methods):
    exec(script, get_globals(context, external_methods), context)
    return context

app.conf.update(results_expires=3600)

if __name__ == '__main__':
    app.start()

