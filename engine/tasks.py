from .celery import app
from .custom_script import lookup_product_info, lookup_shipping_cost


def get_globals(context, external_methods):
    _context = {
        'lookup_product_info': lookup_product_info,
        'lookup_shipping_cost': lookup_shipping_cost,
    }
    _context.update(context)
    _context.update(external_methods)
    return _context

@app.task
def evaluate(expression, context, external_methods):
    return eval(expression, get_globals(context, external_methods))

@app.task
def execute(script, context, external_methods):
    exec(script, get_globals(context, external_methods), context)
    return context
